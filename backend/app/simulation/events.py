from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable

logger = logging.getLogger("nexus.simulation")


class SimSpeed(int, Enum):
    X1 = 1
    X5 = 5
    X10 = 10
    X50 = 50
    X100 = 100


class SimState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    RESET = "reset"


class EventType(str, Enum):
    AGENT_SPAWNED = "AgentSpawned"
    AGENT_WORKING = "AgentWorking"
    AGENT_RESTING = "AgentResting"
    AGENT_IDLE = "AgentIdle"
    AGENT_SEARCHING = "AgentSearching"
    SIMULATION_TICK = "SimulationTick"
    DAILY_RESET = "DailyReset"
    WORLD_UPDATED = "WorldUpdated"
    SPEED_CHANGED = "SpeedChanged"
    SIMULATION_STARTED = "SimulationStarted"
    SIMULATION_PAUSED = "SimulationPaused"
    SIMULATION_RESET = "SimulationReset"


@dataclass
class SimEvent:
    event_type: EventType
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class EventQueue:
    def __init__(self, max_size: int = 1000) -> None:
        self._queue: asyncio.Queue[SimEvent] = asyncio.Queue(maxsize=max_size)
        self._subscribers: dict[EventType, list[Callable]] = {}
        self._all_log: list[dict] = []
        self._eps_counter: int = 0
        self._eps_window_start: float = time.time()

    async def put(self, event: SimEvent) -> None:
        try:
            self._queue.put_nowait(event)
            self._eps_counter += 1
            self._all_log.append(event.to_dict())
            if len(self._all_log) > 500:
                self._all_log = self._all_log[-300:]
            for handler in self._subscribers.get(event.event_type, []):
                try:
                    result = handler(event)
                    if hasattr(result, "__await__"):
                        await result
                except Exception as exc:
                    logger.error("event_handler_error: %s", exc)
            for handler in self._subscribers.get(None, []):
                try:
                    result = handler(event)
                    if hasattr(result, "__await__"):
                        await result
                except Exception as exc:
                    logger.error("event_handler_error: %s", exc)
        except asyncio.QueueFull:
            logger.warning("event_queue_full")

    async def get(self) -> SimEvent:
        return await self._queue.get()

    def subscribe(self, event_type: EventType | None, handler: Callable) -> None:
        self._subscribers.setdefault(event_type, []).append(handler)

    @property
    def events_per_second(self) -> float:
        now = time.time()
        elapsed = now - self._eps_window_start
        if elapsed >= 1.0:
            eps = self._eps_counter / elapsed
            self._eps_counter = 0
            self._eps_window_start = now
            return round(eps, 1)
        return 0.0

    @property
    def recent_events(self) -> list[dict]:
        return self._all_log[-50:]
