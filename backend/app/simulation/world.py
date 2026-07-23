from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from app.simulation.events import EventQueue, EventType, SimEvent

logger = logging.getLogger("nexus.simulation")


@dataclass
class WorldClock:
    day: int = 1
    hour: int = 6
    minute: int = 0
    tick_count: int = 0

    def advance(self, minutes: int = 1) -> bool:
        self.minute += minutes
        day_rolled = False
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        while self.hour >= 24:
            self.hour -= 24
            self.day += 1
            day_rolled = True
        self.tick_count += 1
        return day_rolled

    @property
    def time_str(self) -> str:
        return f"Day {self.day} {self.hour:02d}:{self.minute:02d}"

    @property
    def total_minutes(self) -> int:
        return (self.day - 1) * 24 * 60 + self.hour * 60 + self.minute

    def to_dict(self) -> dict:
        return {
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "tick_count": self.tick_count,
            "time_str": self.time_str,
            "total_minutes": self.total_minutes,
        }

    def reset(self) -> None:
        self.day = 1
        self.hour = 6
        self.minute = 0
        self.tick_count = 0


@dataclass
class WorldState:
    clock: WorldClock = field(default_factory=WorldClock)
    population: int = 0
    running_agents: int = 0
    idle_agents: int = 0
    working_agents: int = 0
    searching_agents: int = 0
    resting_agents: int = 0
    avg_energy: float = 100.0
    avg_reputation: float = 0.0
    total_events: int = 0
    events_per_second: float = 0.0

    def to_dict(self) -> dict:
        return {
            "clock": self.clock.to_dict(),
            "population": self.population,
            "running_agents": self.running_agents,
            "idle_agents": self.idle_agents,
            "working_agents": self.working_agents,
            "searching_agents": self.searching_agents,
            "resting_agents": self.resting_agents,
            "avg_energy": round(self.avg_energy, 1),
            "avg_reputation": round(self.avg_reputation, 2),
            "total_events": self.total_events,
            "events_per_second": self.events_per_second,
        }

    def reset(self) -> None:
        self.clock.reset()
        self.population = 0
        self.running_agents = 0
        self.idle_agents = 0
        self.working_agents = 0
        self.searching_agents = 0
        self.resting_agents = 0
        self.avg_energy = 100.0
        self.avg_reputation = 0.0
        self.total_events = 0
        self.events_per_second = 0.0


class World:
    def __init__(self, event_queue: EventQueue) -> None:
        self.state = WorldState()
        self.events = event_queue

    def update_stats(self, agents: list) -> None:
        self.state.population = len(agents)
        states = {}
        energies = []
        reputations = []
        for a in agents:
            s = a.current_status
            states[s] = states.get(s, 0) + 1
            energies.append(a.energy)
            reputations.append(a.reputation)
        self.state.idle_agents = states.get("idle", 0)
        self.state.working_agents = states.get("working", 0)
        self.state.searching_agents = states.get("searching", 0)
        self.state.resting_agents = states.get("resting", 0)
        self.state.running_agents = len(agents)
        self.state.avg_energy = sum(energies) / len(energies) if energies else 0
        self.state.avg_reputation = sum(reputations) / len(reputations) if reputations else 0
        self.state.events_per_second = self.events.events_per_second

    def to_dict(self) -> dict:
        return self.state.to_dict()

    def reset(self) -> None:
        self.state.reset()
