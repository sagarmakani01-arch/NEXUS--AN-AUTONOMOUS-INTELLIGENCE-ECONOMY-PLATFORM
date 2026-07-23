from typing import Optional

from app.temporal.persistence import temporal_persistence
from app.temporal.history import history_manager
from app.temporal.snapshots import snapshot_manager


class ReplayEngine:
    """Replays historical timelines without modifying original history."""

    def __init__(self):
        self._replaying: bool = False
        self._replay_speed: float = 1.0
        self._replay_position: int = 0
        self._replay_start_tick: int = 0
        self._replay_end_tick: int = 0

    @property
    def is_replaying(self) -> bool:
        return self._replaying

    async def start_replay(
        self,
        clock_id: str,
        start_tick: int = 0,
        end_tick: int = None,
        speed: float = 1.0,
        timeline_id: str = None,
    ) -> dict:
        if self._replaying:
            return {"error": "Replay already in progress"}

        total_events = await history_manager.get_total_events(clock_id, timeline_id)
        if total_events == 0:
            return {"error": "No events to replay"}

        if end_tick is None:
            events = await history_manager.query(clock_id=clock_id, timeline_id=timeline_id, limit=1)
            if events:
                end_tick = events[-1].get("tick", 1000)
            else:
                end_tick = 1000

        self._replaying = True
        self._replay_speed = max(0.1, min(10.0, speed))
        self._replay_position = start_tick
        self._replay_start_tick = start_tick
        self._replay_end_tick = end_tick

        return {
            "started": True,
            "start_tick": start_tick,
            "end_tick": end_tick,
            "speed": self._replay_speed,
            "total_events": total_events,
        }

    async def step(self, clock_id: str, timeline_id: str = None) -> Optional[dict]:
        if not self._replaying:
            return None

        if self._replay_position >= self._replay_end_tick:
            self._replaying = False
            return {"finished": True, "position": self._replay_position}

        events = await history_manager.query_in_range(
            clock_id=clock_id,
            start_tick=self._replay_position,
            end_tick=self._replay_position + 1,
            timeline_id=timeline_id,
        )

        snapshot = await snapshot_manager.get_closest(clock_id, self._replay_position, timeline_id)

        self._replay_position += 1

        return {
            "tick": self._replay_position,
            "events": events,
            "snapshot": snapshot,
            "progress": (self._replay_position - self._replay_start_tick)
            / max(1, self._replay_end_tick - self._replay_start_tick),
        }

    async def jump_to(self, tick: int) -> dict:
        if not self._replaying:
            return {"error": "No replay in progress"}

        if tick < self._replay_start_tick or tick > self._replay_end_tick:
            return {"error": "Tick out of replay range"}

        self._replay_position = tick
        return {"jumped_to": tick, "progress": (tick - self._replay_start_tick) / max(1, self._replay_end_tick - self._replay_start_tick)}

    async def stop(self) -> dict:
        was_replaying = self._replaying
        self._replaying = False
        self._replay_position = 0
        return {"stopped": was_replaying}

    async def set_speed(self, speed: float) -> dict:
        self._replay_speed = max(0.1, min(10.0, speed))
        return {"speed": self._replay_speed}

    def get_state(self) -> dict:
        return {
            "replaying": self._replaying,
            "speed": self._replay_speed,
            "position": self._replay_position,
            "start_tick": self._replay_start_tick,
            "end_tick": self._replay_end_tick,
            "progress": (self._replay_position - self._replay_start_tick)
            / max(1, self._replay_end_tick - self._replay_start_tick)
            if self._replaying
            else 0,
        }


replay_engine = ReplayEngine()
