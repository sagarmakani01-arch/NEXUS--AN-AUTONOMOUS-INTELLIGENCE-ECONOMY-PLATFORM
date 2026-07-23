import random
from datetime import datetime

from app.compute.persistence import compute_db


class ComputeScheduler:
    PRIORITY_LEVELS = ["high", "medium", "low"]

    async def assign_task(self, task_type: str, description: str = None,
                          priority: str = "medium", source: str = None,
                          payload: dict = None, node_id: str = None) -> dict:
        if not node_id:
            node = await compute_db.get_available_node()
            node_id = node["id"] if node else None
        task = await compute_db.create_task(
            node_id=node_id,
            task_type=task_type,
            description=description or f"Compute task: {task_type}",
            priority=priority,
            status="assigned" if node_id else "pending",
            source=source,
            payload=__import__("json").dumps(payload or {}),
        )
        if node_id:
            node_data = await compute_db.get_node(node_id)
            if node_data:
                await compute_db.update_node(
                    node_id, active_tasks=(node_data["active_tasks"] or 0) + 1)
        return task

    async def complete_task(self, task_id: str, result: str = None) -> dict | None:
        task = await compute_db.update_task(
            task_id,
            status="completed",
            result=result,
            progress=1.0,
            completed_at=datetime.utcnow(),
        )
        if task and task["node_id"]:
            node = await compute_db.get_node(task["node_id"])
            if node:
                await compute_db.update_node(
                    task["node_id"],
                    active_tasks=max(0, (node["active_tasks"] or 0) - 1))
        return task

    async def fail_task(self, task_id: str, error: str = None) -> dict | None:
        return await compute_db.update_task(
            task_id, status="failed", result=error)

    async def list_tasks(self, node_id: str = None, status: str = None) -> list[dict]:
        return await compute_db.get_tasks(node_id, status)

    async def set_agent_priority(self, agent_id: str, priority: str = "medium",
                                 reason: str = None, node_id: str = None) -> dict:
        return await compute_db.set_agent_priority(
            agent_id=agent_id,
            priority=priority,
            reason=reason or f"Auto-assigned {priority} priority",
            assigned_node_id=node_id,
        )

    async def get_agent_priorities(self, node_id: str = None, priority: str = None) -> list[dict]:
        return await compute_db.get_agent_priorities(node_id, priority)

    async def get_scheduler_stats(self) -> dict:
        tasks = await compute_db.get_tasks()
        pending = len([t for t in tasks if t["status"] == "pending"])
        running = len([t for t in tasks if t["status"] == "assigned"])
        completed = len([t for t in tasks if t["status"] == "completed"])
        failed = len([t for t in tasks if t["status"] == "failed"])
        return {
            "total": len(tasks),
            "pending": pending,
            "running": running,
            "completed": completed,
            "failed": failed,
        }


scheduler = ComputeScheduler()
