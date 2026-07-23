from __future__ import annotations

import asyncio
import logging

from app.execution.capabilities import capability_system
from app.execution.collaboration import collaboration
from app.execution.failure import failure_handler
from app.execution.goal_decomposition import goal_decomposition
from app.execution.learning import learning
from app.execution.orchestrator import orchestrator
from app.execution.persistence import get_execution_stats
from app.execution.quality import quality_evaluation
from app.execution.tools import tool_system
from app.execution.workspace import work_environment

logger = logging.getLogger("nexus.execution.engine")


class ExecutionEngine:
    def __init__(self) -> None:
        self._running = False
        self._task: asyncio.Task | None = None
        self._tick_interval = 15.0

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        await tool_system.ensure_tools()
        self._task = asyncio.create_task(self._run_loop())
        logger.info("execution_engine_started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("execution_engine_stopped")

    async def _run_loop(self) -> None:
        try:
            while self._running:
                await self._tick()
                await asyncio.sleep(self._tick_interval)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("execution_engine_loop_error: %s", exc)

    async def _tick(self) -> None:
        try:
            await self._process_active_projects()
        except Exception as exc:
            logger.error("execution_tick_error: %s", exc)

    async def _process_active_projects(self) -> None:
        active = orchestrator.get_active_projects()
        for project_id, info in list(active.items()):
            if info.get("status") == "executing":
                ready = await goal_decomposition.get_ready_tasks(project_id)
                if ready:
                    await orchestrator._execute_task(ready[0])

    async def execute_goal(self, agent_id: str, goal: str, title: str = "") -> dict:
        return await orchestrator.execute_project(agent_id, title or goal, goal)

    async def create_project(self, agent_id: str, title: str, goal: str = "", **kwargs) -> dict:
        return await orchestrator.create_project(agent_id, title, goal=goal, **kwargs)

    async def get_project(self, project_id: str) -> dict | None:
        return await orchestrator.get_project_status(project_id)

    async def list_projects(self, agent_id: str = "", status: str = "") -> list[dict]:
        from app.execution.persistence import list_projects
        return await list_projects(agent_id=agent_id, status=status)

    async def start_project(self, project_id: str) -> dict:
        return await orchestrator.start_execution(project_id)

    async def pause_project(self, project_id: str) -> dict:
        return await orchestrator.pause_execution(project_id)

    async def resume_project(self, project_id: str) -> dict:
        return await orchestrator.resume_execution(project_id)

    async def get_agent_execution_state(self, agent_id: str) -> dict:
        caps = await capability_system.get_agent_profile(agent_id)
        projects = await orchestrator.list_projects(agent_id=agent_id)
        workspaces = await work_environment.list_agent_workspaces(agent_id)
        stats = await learning.get_agent_learning_stats(agent_id)
        return {
            "capabilities": caps,
            "projects": projects,
            "workspaces": workspaces,
            "learning_stats": stats,
        }

    async def get_full_state(self) -> dict:
        stats = await get_execution_stats()
        engine_stats = orchestrator.get_stats()
        active = orchestrator.get_active_projects()
        return {
            "db_stats": stats,
            "engine_stats": engine_stats,
            "active_projects": len(active),
            "running": self._running,
        }

    def get_state(self) -> dict:
        return {
            "running": self._running,
            "stats": orchestrator.get_stats(),
            "active_projects": len(orchestrator.get_active_projects()),
        }


execution_engine = ExecutionEngine()
