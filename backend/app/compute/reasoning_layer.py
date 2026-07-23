import json
import random

from app.compute.persistence import compute_db


class ReasoningLayer:
    DEDICATED_TYPES = ["llm_request", "agent_planning", "research_task", "reflection", "decision"]

    async def assign_reasoning_task(self, agent_id: str, task_type: str,
                                    payload: dict = None) -> dict:
        gpu_node = await self._find_gpu_node()
        if not gpu_node:
            gpu_node = await compute_db.get_available_node()
        task = await compute_db.create_task(
            node_id=gpu_node["id"] if gpu_node else None,
            task_type=f"reasoning_{task_type}",
            description=f"AI reasoning task for agent {agent_id[:8]}",
            priority="high",
            source="reasoning_layer",
            payload=json.dumps(payload or {"agent_id": agent_id, "task_type": task_type}),
            status="assigned" if gpu_node else "pending",
        )
        return task

    async def _find_gpu_node(self) -> dict | None:
        nodes = await compute_db.list_nodes("online")
        for n in nodes:
            if n.get("gpu_count", 0) > 0 and (n.get("gpu_usage", 1.0) or 1.0) < 0.8:
                return n
        return None

    async def get_layer_stats(self) -> dict:
        tasks = await compute_db.get_tasks()
        reasoning_tasks = [t for t in tasks if t["task_type"].startswith("reasoning_")]
        return {
            "total_reasoning_tasks": len(reasoning_tasks),
            "active_reasoning": len([t for t in reasoning_tasks if t["status"] == "assigned"]),
            "completed_reasoning": len([t for t in reasoning_tasks if t["status"] == "completed"]),
            "gpu_nodes_available": len([n for n in await compute_db.list_nodes("online") if n.get("gpu_count", 0) > 0]),
        }


reasoning_layer = ReasoningLayer()
