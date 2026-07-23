import random
from datetime import datetime

from app.compute.persistence import compute_db


class SyncEngine:
    async def synchronize(self, source_node_id: str, target_node_id: str,
                          sync_type: str = "state") -> dict:
        data_size = random.randint(1024, 102400)
        duration = round(data_size / 1024 * random.uniform(1, 10), 1)
        sync = await compute_db.create_sync(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            sync_type=sync_type,
            status="completed",
            data_size_bytes=data_size,
            duration_ms=duration,
            completed_at=datetime.utcnow(),
        )
        return sync

    async def get_sync_history(self, node_id: str = None) -> list[dict]:
        return await compute_db.get_sync_history(node_id)

    async def sync_distributed_clock(self) -> dict:
        clock = await compute_db.get_or_create_clock()
        updated = await compute_db.update_clock(
            clock["clock_name"],
            tick_count=(clock["tick_count"] or 0) + 1,
            time_scale=1.0,
            last_sync_at=datetime.utcnow(),
        )
        return updated or clock

    async def get_clock_state(self) -> dict:
        return await compute_db.get_or_create_clock()

    async def get_sync_stats(self) -> dict:
        history = await compute_db.get_sync_history()
        total = len(history)
        completed = len([s for s in history if s["status"] == "completed"])
        return {
            "total_syncs": total,
            "completed_syncs": completed,
            "total_data_bytes": sum(s["data_size_bytes"] for s in history),
            "total_duration_ms": sum(s["duration_ms"] for s in history),
        }


sync_engine = SyncEngine()
