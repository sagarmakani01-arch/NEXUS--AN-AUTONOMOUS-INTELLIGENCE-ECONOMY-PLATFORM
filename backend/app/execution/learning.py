from __future__ import annotations

import logging

from app.execution import persistence as ep
from app.execution.capabilities import capability_system

logger = logging.getLogger("nexus.execution.learning")


class LearningFromWork:
    async def learn_from_task(self, task_id: str, agent_id: str, project_id: str) -> dict:
        task = await ep.get_execution_task(task_id)
        if not task:
            return {"error": "Task not found"}

        success = task.get("status") == "completed"
        skills_used = task.get("required_skills", [])
        duration = task.get("actual_duration", 0)

        skill_updates = []
        for skill in skills_used:
            update = await capability_system.update_after_task(
                agent_id, skill, success, duration,
            )
            skill_updates.append(update)

        memory_update = await self._create_work_memory(agent_id, task, success)
        timeline_update = await self._create_timeline_event(agent_id, task, project_id, success)

        return {
            "task_id": task_id,
            "agent_id": agent_id,
            "success": success,
            "skills_updated": len(skill_updates),
            "skill_details": skill_updates,
            "memory_created": memory_update.get("created", False),
            "timeline_event": timeline_update.get("created", False),
        }

    async def learn_from_project(self, project_id: str, agent_id: str) -> dict:
        results = await ep.list_execution_results(project_id=project_id, agent_id=agent_id)
        if not results:
            return {"project_id": project_id, "lessons": []}

        completed = [r for r in results if r["status"] == "completed"]
        failed = [r for r in results if r["status"] == "failed"]
        all_lessons = []
        for r in results:
            lessons = r.get("lessons_learned", [])
            if isinstance(lessons, str):
                import json
                try:
                    lessons = json.loads(lessons)
                except (json.JSONDecodeError, TypeError):
                    lessons = []
            all_lessons.extend(lessons)

        project_summary = {
            "total_tasks": len(results),
            "completed": len(completed),
            "failed": len(failed),
            "avg_quality": round(sum(r["quality_score"] for r in results) / len(results), 2),
            "lessons_learned": all_lessons[:10],
        }

        await self._create_project_memory(agent_id, project_id, project_summary)
        return project_summary

    async def get_agent_learning_stats(self, agent_id: str) -> dict:
        caps = await ep.get_capabilities(agent_id)
        results = await ep.list_execution_results(agent_id=agent_id)

        total_tasks = len(results)
        completed = len([r for r in results if r["status"] == "completed"])
        total_lessons = 0
        for r in results:
            lessons = r.get("lessons_learned", [])
            if isinstance(lessons, str):
                import json
                try:
                    lessons = json.loads(lessons)
                except (json.JSONDecodeError, TypeError):
                    lessons = []
            total_lessons += len(lessons)

        total_experience = sum(c["experience"] for c in caps)
        avg_success = sum(c["success_rate"] for c in caps) / max(len(caps), 1)

        return {
            "agent_id": agent_id,
            "total_tasks_executed": total_tasks,
            "tasks_completed": completed,
            "completion_rate": round(completed / max(total_tasks, 1) * 100, 1),
            "total_skills": len(caps),
            "total_experience": round(total_experience, 1),
            "avg_success_rate": round(avg_success, 2),
            "total_lessons_learned": total_lessons,
            "expert_skills": len([c for c in caps if c["level"] == "expert"]),
            "advanced_skills": len([c for c in caps if c["level"] == "advanced"]),
        }

    async def _create_work_memory(self, agent_id: str, task: dict, success: bool) -> dict:
        try:
            from app.simulation.persistence import save_memory
            title = f"Completed: {task['title']}" if success else f"Failed: {task['title']}"
            desc = f"Task {'succeeded' if success else 'failed'} with quality {task.get('quality_score', 0):.2f}"
            importance = "high" if success else "medium"
            await save_memory(agent_id, "work", importance, title, desc)
            return {"created": True}
        except Exception:
            return {"created": False}

    async def _create_timeline_event(self, agent_id: str, task: dict, project_id: str, success: bool) -> dict:
        try:
            from app.simulation.persistence import save_timeline_event
            from app.simulation.engine import engine as sim_engine
            current_day = sim_engine.world.state.clock.day if sim_engine._started_at else 1
            event_type = "TaskCompleted" if success else "TaskFailed"
            title = f"{'Completed' if success else 'Failed'}: {task['title']}"
            await save_timeline_event(agent_id, current_day, event_type, title)
            return {"created": True}
        except Exception:
            return {"created": False}

    async def _create_project_memory(self, agent_id: str, project_id: str, summary: dict) -> dict:
        try:
            from app.simulation.persistence import save_memory
            title = f"Project completed: {summary['completed']}/{summary['total_tasks']} tasks"
            desc = f"Avg quality: {summary['avg_quality']}, Lessons: {len(summary['lessons_learned'])}"
            await save_memory(agent_id, "project", "high", title, desc)
            return {"created": True}
        except Exception:
            return {"created": False}


learning = LearningFromWork()
