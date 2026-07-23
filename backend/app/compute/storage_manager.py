import random

from app.compute.persistence import compute_db


class StorageManager:
    async def record_storage(self, node_id: str, storage_type: str = "local",
                             total_bytes: int = 0, used_bytes: int = 0,
                             data_type: str = "simulation") -> dict:
        return await compute_db.record_storage(
            node_id=node_id,
            storage_type=storage_type,
            total_bytes=total_bytes or random.randint(1024, 102400),
            used_bytes=used_bytes or random.randint(100, 50000),
            data_type=data_type,
        )

    async def get_storage(self, node_id: str) -> list[dict]:
        return await compute_db.get_storage(node_id)

    async def get_all_storage(self) -> dict:
        nodes = await compute_db.list_nodes()
        all_storage = []
        for n in nodes:
            storage = await compute_db.get_storage(n["id"])
            all_storage.extend(storage)
        total = sum(s["total_bytes"] for s in all_storage)
        used = sum(s["used_bytes"] for s in all_storage)
        return {
            "total_bytes": total,
            "used_bytes": used,
            "available_bytes": total - used,
            "usage_pct": round(used / max(1, total) * 100, 1),
            "nodes_with_storage": len(all_storage),
        }


storage_manager = StorageManager()
