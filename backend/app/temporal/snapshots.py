import json
from typing import Optional

from app.temporal.persistence import temporal_persistence


class SnapshotManager:
    """Captures and restores world state snapshots for replay and timeline branching."""

    def __init__(self):
        self._last_snapshot_tick: int = 0
        self._snapshot_interval: int = 100

    async def capture(
        self,
        clock_id: str,
        tick: int,
        year: int,
        world_state: dict,
        label: str = None,
        timeline_id: str = None,
    ) -> dict:
        snapshot = await temporal_persistence.create_snapshot(
            clock_id=clock_id,
            tick=tick,
            year=year,
            full_state=world_state,
            label=label,
            timeline_id=timeline_id,
        )
        self._last_snapshot_tick = tick
        return {
            "id": snapshot.id,
            "tick": tick,
            "year": year,
            "label": snapshot.label,
        }

    async def should_snapshot(self, current_tick: int) -> bool:
        return (current_tick - self._last_snapshot_tick) >= self._snapshot_interval

    async def get_all(self, clock_id: str, timeline_id: str = None) -> list[dict]:
        snapshots = await temporal_persistence.get_snapshots(clock_id, timeline_id)
        return [
            {
                "id": s.id,
                "tick": s.tick,
                "year": s.year,
                "label": s.label,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in snapshots
        ]

    async def get_by_id(self, snapshot_id: str) -> Optional[dict]:
        snapshot = await temporal_persistence.get_snapshot(snapshot_id)
        if not snapshot:
            return None
        return {
            "id": snapshot.id,
            "tick": snapshot.tick,
            "year": snapshot.year,
            "label": snapshot.label,
            "full_state": json.loads(snapshot.full_state),
            "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        }

    async def get_closest(self, clock_id: str, tick: int, timeline_id: str = None) -> Optional[dict]:
        snapshot = await temporal_persistence.get_closest_snapshot(clock_id, tick, timeline_id)
        if not snapshot:
            return None
        return {
            "id": snapshot.id,
            "tick": snapshot.tick,
            "year": snapshot.year,
            "label": snapshot.label,
            "full_state": json.loads(snapshot.full_state),
        }

    async def get_state_at_tick(self, clock_id: str, tick: int, timeline_id: str = None) -> Optional[dict]:
        snapshot = await temporal_persistence.get_closest_snapshot(clock_id, tick, timeline_id)
        if not snapshot:
            return None
        return json.loads(snapshot.full_state)

    def set_interval(self, interval: int):
        self._snapshot_interval = max(10, interval)

    def get_stats(self) -> dict:
        return {
            "last_snapshot_tick": self._last_snapshot_tick,
            "snapshot_interval": self._snapshot_interval,
        }


snapshot_manager = SnapshotManager()
