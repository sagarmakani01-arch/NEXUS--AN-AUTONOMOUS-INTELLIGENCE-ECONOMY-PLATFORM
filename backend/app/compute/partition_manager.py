import random

from app.compute.persistence import compute_db


class PartitionManager:
    PARTITION_TYPES = ["planet", "region", "civilization", "time_period", "task_domain"]

    async def create_partition(self, partition_key: str, partition_type: str = "region",
                               universe_id: str = None, parent_id: str = None) -> dict:
        node = await compute_db.get_available_node()
        partition = await compute_db.create_partition(
            node_id=node["id"] if node else None,
            partition_key=partition_key,
            partition_type=partition_type,
            universe_id=universe_id,
            parent_partition_id=parent_id,
            status="assigned" if node else "unassigned",
            agent_count=random.randint(10, 500),
            workload_score=round(random.uniform(0.1, 0.8), 2),
        )
        return partition

    async def list_partitions(self, node_id: str = None) -> list[dict]:
        return await compute_db.get_partitions(node_id)

    async def reassign_partition(self, partition_id: str, new_node_id: str = None) -> dict | None:
        if not new_node_id:
            node = await compute_db.get_available_node()
            new_node_id = node["id"] if node else None
        return await compute_db.update_partition(
            partition_id,
            node_id=new_node_id,
            status="assigned" if new_node_id else "unassigned",
        )

    async def get_partition_stats(self) -> dict:
        partitions = await compute_db.get_partitions()
        total = len(partitions)
        assigned = len([p for p in partitions if p["node_id"]])
        by_type: dict[str, int] = {}
        for p in partitions:
            by_type[p["partition_type"]] = by_type.get(p["partition_type"], 0) + 1
        return {"total": total, "assigned": assigned, "unassigned": total - assigned, "by_type": by_type}


partition_manager = PartitionManager()
