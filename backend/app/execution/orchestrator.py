from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from datetime import datetime, timezone

from app.execution import persistence as ep
from app.execution.capabilities import capability_system
from app.execution.collaboration import collaboration
from app.execution.failure import failure_handler
from app.execution.goal_decomposition import goal_decomposition
from app.execution.learning import learning
from app.execution.quality import quality_evaluation
from app.execution.tools import tool_system
from app.execution.workspace import work_environment

logger = logging.getLogger("nexus.execution.orchestrator")


class ExecutionOrchestrator:
    def __init__(self) -> None:
        self._active_projects: dict[str, dict] = {}
        self._task_queue: asyncio.Queue | None = None
        self._running = False
        self._stats = {
            "projects_created": 0,
            "tasks_executed": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tools_used": 0,
        }

    async def create_project(
        self, agent_id: str, title: str, description: str = "",
        goal: str = "", contract_id: str | None = None,
        priority: str = "medium", estimated_cost: float = 0,
    ) -> dict:
        project = await ep.create_project(
            agent_id=agent_id, title=title, description=description or goal,
            contract_id=contract_id, priority=priority, estimated_cost=estimated_cost,
        )

        ws = await work_environment.create_workspace(agent_id, project["id"], f"WS-{title[:20]}")

        profile = await capability_system.get_agent_profile(agent_id)
        agent_skills = [c["skill_name"] for c in profile.get("capabilities", [])]

        tasks = await goal_decomposition.decompose_goal(project["id"], goal or title, agent_skills)

        project_cost = await goal_decomposition.estimate_project_cost(project["id"])
        await ep.update_project(
            project["id"],
            estimated_cost=project_cost["total_estimated_cost"],
            metadata_json=json.dumps({"workspace_id": ws.get("id"), "goal": goal}),
        )

        self._active_projects[project["id"]] = {
            "agent_id": agent_id,
            "workspace_id": ws.get("id"),
            "status": "planning",
        }
        self._stats["projects_created"] += 1
        logger.info("project_created project=%s agent=%s tasks=%d", project["id"], agent_id, len(tasks))
        return {**project, "tasks": tasks, "workspace": ws, "cost_estimate": project_cost}

    async def get_project_status(self, project_id: str) -> dict | None:
        project = await ep.get_project(project_id)
        if not project:
            return None
        tasks = await ep.list_execution_tasks(project_id=project_id)
        results = await ep.list_execution_results(project_id=project_id)
        return {
            "project": project,
            "tasks": tasks,
            "results": results,
            "completion_stats": {
                "total": len(tasks),
                "completed": len([t for t in tasks if t["status"] == "completed"]),
                "failed": len([t for t in tasks if t["status"] == "failed"]),
                "in_progress": len([t for t in tasks if t["status"] == "running"]),
                "created": len([t for t in tasks if t["status"] == "created"]),
            },
        }

    async def start_execution(self, project_id: str) -> dict:
        project = await ep.get_project(project_id)
        if not project:
            return {"error": "Project not found"}
        await ep.update_project(project_id, status="executing")
        if project_id in self._active_projects:
            self._active_projects[project_id]["status"] = "executing"
        ready_tasks = await goal_decomposition.get_ready_tasks(project_id)
        for task in ready_tasks[:3]:
            await self._execute_task(task)
        return {"project_id": project_id, "status": "executing", "tasks_started": min(len(ready_tasks), 3)}

    async def pause_execution(self, project_id: str) -> dict:
        await ep.update_project(project_id, status="paused")
        if project_id in self._active_projects:
            self._active_projects[project_id]["status"] = "paused"
        return {"project_id": project_id, "status": "paused"}

    async def resume_execution(self, project_id: str) -> dict:
        await ep.update_project(project_id, status="executing")
        if project_id in self._active_projects:
            self._active_projects[project_id]["status"] = "executing"
        ready_tasks = await goal_decomposition.get_ready_tasks(project_id)
        for task in ready_tasks[:3]:
            await self._execute_task(task)
        return {"project_id": project_id, "status": "executing", "tasks_queued": len(ready_tasks)}

    async def _execute_task(self, task: dict) -> dict:
        task_id = task["id"]
        project_id = task["project_id"]
        agent_id = task.get("agent_id")

        await ep.update_execution_task(task_id, status="running", started_at=datetime.now(timezone.utc))
        self._stats["tasks_executed"] += 1

        try:
            tools_used = []
            for skill in task.get("required_skills", [])[:2]:
                tool_name = self._skill_to_tool(skill)
                if tool_name:
                    result = await tool_system.execute_tool(tool_name, agent_id or "system", {"skill": skill})
                    if "error" not in result:
                        tools_used.append(tool_name)
                        self._stats["tools_used"] += 1

            success = random.random() < 0.75
            duration = random.randint(task.get("estimated_duration", 4) // 2, task.get("estimated_duration", 4) * 2)
            cost = task.get("estimated_cost", 10) * random.uniform(0.8, 1.3)

            if success:
                quality = round(random.uniform(0.5, 1.0), 2)
                await ep.update_execution_task(
                    task_id, status="completed", actual_duration=duration,
                    actual_cost=round(cost, 2), quality_score=quality,
                    result=f"Task completed successfully. Quality: {quality}",
                    completed_at=datetime.now(timezone.utc),
                )
                self._stats["tasks_completed"] += 1

                if agent_id:
                    eval_result = await quality_evaluation.evaluate_task(task_id, agent_id, project_id)
                    await learning.learn_from_task(task_id, agent_id, project_id)

                await self._update_project_progress(project_id)
                await self._try_next_tasks(project_id)

                return {"status": "completed", "quality": quality, "duration": duration, "tools_used": tools_used}
            else:
                error = random.choice(["Timeout exceeded", "Resource unavailable", "Invalid input format", "Dependency failed"])
                failure_result = await failure_handler.handle_task_failure(task_id, error)
                self._stats["tasks_failed"] += 1
                return {"status": "failed", "error": error, "recovery": failure_result}

        except Exception as exc:
            logger.error("task_execution_error task=%s err=%s", task_id, exc)
            await ep.update_execution_task(task_id, status="failed", error_message=str(exc))
            self._stats["tasks_failed"] += 1
            return {"status": "error", "error": str(exc)}

    async def _update_project_progress(self, project_id: str) -> None:
        tasks = await ep.list_execution_tasks(project_id=project_id)
        total = len(tasks)
        completed = len([t for t in tasks if t["status"] == "completed"])
        failed = len([t for t in tasks if t["status"] == "failed"])
        progress = round(completed / max(total, 1) * 100, 1)
        await ep.update_project(
            project_id, completed_tasks=completed, failed_tasks=failed, progress=progress,
        )
        if completed == total and total > 0:
            await ep.update_project(project_id, status="completed", completed_at=datetime.now(timezone.utc))
            if project_id in self._active_projects:
                self._active_projects[project_id]["status"] = "completed"

    async def _try_next_tasks(self, project_id: str) -> None:
        ready = await goal_decomposition.get_ready_tasks(project_id)
        for task in ready[:2]:
            await self._execute_task(task)

    def _skill_to_tool(self, skill: str) -> str | None:
        mapping = {
            "Python": "code_executor", "JavaScript": "code_executor",
            "React": "code_executor", "Machine Learning": "data_analyzer",
            "Data Analysis": "data_analyzer", "Statistics": "data_analyzer",
            "API Development": "api_client", "Testing": "test_runner",
            "DevOps": "deployment_manager", "System Design": "file_manager",
            "Writing": "document_generator", "Research": "web_search",
        }
        return mapping.get(skill)

    async def execute_project(self, agent_id: str, title: str, goal: str, **kwargs) -> dict:
        project = await self.create_project(agent_id, title, goal=goal, **kwargs)
        if "error" in project:
            return project
        result = await self.start_execution(project["id"])
        return {"project": project, "execution": result}

    def get_stats(self) -> dict:
        return self._stats

    def get_active_projects(self) -> dict:
        return self._active_projects


orchestrator = ExecutionOrchestrator()
