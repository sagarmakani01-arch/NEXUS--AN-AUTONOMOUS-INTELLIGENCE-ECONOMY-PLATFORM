import random
import time

from app.compute.persistence import compute_db


class NodeManager:
    async def register_node(self, name: str, node_type: str = "worker",
                            cpu_cores: int = 4, gpu_count: int = 0,
                            memory_total_mb: float = 4096, max_tasks: int = 10,
                            host: str = None, port: int = 0) -> dict:
        existing = await compute_db.list_nodes()
        node = await compute_db.register_node(
            name=name,
            node_type=node_type,
            status="online",
            host=host or f"192.168.1.{len(existing) + 1}",
            port=port or (8001 + len(existing)),
            cpu_cores=cpu_cores,
            gpu_count=gpu_count,
            memory_total_mb=memory_total_mb,
            max_tasks=max_tasks,
            cpu_usage=random.uniform(5, 30),
            memory_used_mb=random.uniform(100, 500),
            network_latency_ms=round(random.uniform(1, 20), 1),
            uptime_seconds=0,
        )
        await compute_db.add_capability(
            node_id=node["id"],
            capability_type="simulation",
            description=f"Simulation engine for {name}",
            performance_score=round(random.uniform(0.5, 1.0), 2),
        )
        if node_type == "gpu":
            await compute_db.add_capability(
                node_id=node["id"],
                capability_type="ai_reasoning",
                description="GPU-accelerated AI reasoning",
                performance_score=round(random.uniform(0.7, 1.0), 2),
            )
        if gpu_count > 0:
            await compute_db.add_capability(
                node_id=node["id"],
                capability_type="rendering",
                description=f"3D rendering ({gpu_count} GPUs)",
                performance_score=round(random.uniform(0.6, 0.9), 2),
            )
        return node

    async def remove_node(self, node_id: str) -> bool:
        return await compute_db.remove_node(node_id)

    async def get_node(self, node_id: str) -> dict | None:
        return await compute_db.get_node(node_id)

    async def list_nodes(self, status: str = None) -> list[dict]:
        return await compute_db.list_nodes(status)

    async def heartbeat(self, node_id: str) -> dict | None:
        return await compute_db.update_node(
            node_id,
            last_heartbeat=__import__("datetime").datetime.utcnow(),
            status="online",
            uptime_seconds=random.uniform(100, 10000),
        )

    async def mark_offline(self, node_id: str) -> dict | None:
        return await compute_db.update_node(node_id, status="offline")

    async def get_available_node(self) -> dict | None:
        return await compute_db.get_available_node()


node_manager = NodeManager()
