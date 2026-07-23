import asyncio
from datetime import datetime
from typing import Optional

from app.temporal.persistence import temporal_persistence
from app.domain.models.temporal import TemporalClock


class TemporalClock:
    """Deterministic simulation clock supporting ticks, minutes, hours, days, years, centuries."""

    TICKS_PER_MINUTE = 1
    MINUTES_PER_HOUR = 60
    HOURS_PER_DAY = 24
    DAYS_PER_YEAR = 365
    YEARS_PER_CENTURY = 100

    def __init__(self):
        self._clock_id: Optional[str] = None
        self._tick_count: int = 0
        self._current_year: int = 2025
        self._current_day: int = 1
        self._current_hour: int = 0
        self._time_scale: float = 1.0
        self._paused: bool = False
        self._running: bool = False
        self._lock = asyncio.Lock()

    @property
    def tick_count(self) -> int:
        return self._tick_count

    @property
    def current_year(self) -> int:
        return self._current_year

    @property
    def current_day(self) -> int:
        return self._current_day

    @property
    def current_hour(self) -> int:
        return self._current_hour

    @property
    def time_scale(self) -> float:
        return self._time_scale

    @property
    def paused(self) -> bool:
        return self._paused

    @property
    def running(self) -> bool:
        return self._running

    def get_time_string(self) -> str:
        return f"Year {self._current_year}, Day {self._current_day}, Hour {self._current_hour}"

    def get_century(self) -> int:
        return (self._current_year - 1) // self.YEARS_PER_CENTURY + 1

    async def initialize(self) -> str:
        clock = await temporal_persistence.get_active_clock()
        if clock:
            self._clock_id = clock.id
            self._tick_count = clock.tick_count
            self._current_year = clock.current_year
            self._current_day = clock.current_day
            self._current_hour = clock.current_hour
            self._time_scale = clock.time_scale
            self._paused = clock.paused
        else:
            clock = await temporal_persistence.create_clock("NexusTemporal", 1.0)
            self._clock_id = clock.id
        return self._clock_id

    async def advance(self, ticks: int = 1) -> dict:
        async with self._lock:
            if self._paused:
                return {"advanced": 0, "time": self.get_time_string()}

            total_advanced = 0
            for _ in range(ticks):
                self._tick_count += 1
                self._current_hour += 1
                total_advanced += 1

                if self._current_hour >= self.HOURS_PER_DAY:
                    self._current_hour = 0
                    self._current_day += 1

                if self._current_day > self.DAYS_PER_YEAR:
                    self._current_day = 1
                    self._current_year += 1

            await temporal_persistence.update_clock(
                self._clock_id,
                tick_count=self._tick_count,
                current_year=self._current_year,
                current_day=self._current_day,
                current_hour=self._current_hour,
            )

            return {
                "advanced": total_advanced,
                "tick_count": self._tick_count,
                "year": self._current_year,
                "day": self._current_day,
                "hour": self._current_hour,
                "century": self.get_century(),
                "time": self.get_time_string(),
            }

    async def jump_to_year(self, year: int) -> dict:
        async with self._lock:
            ticks_needed = (year - self._current_year) * self.DAYS_PER_YEAR * self.HOURS_PER_DAY
            if ticks_needed < 0:
                return {"error": "Cannot jump backwards in time"}

            self._current_year = year
            self._current_day = 1
            self._current_hour = 0
            self._tick_count += ticks_needed

            await temporal_persistence.update_clock(
                self._clock_id,
                tick_count=self._tick_count,
                current_year=self._current_year,
                current_day=self._current_day,
                current_hour=self._current_hour,
            )

            return {
                "jumped": True,
                "tick_count": self._tick_count,
                "year": self._current_year,
                "time": self.get_time_string(),
            }

    async def pause(self):
        async with self._lock:
            self._paused = True
            await temporal_persistence.update_clock(self._clock_id, paused=True)
            return {"paused": True, "time": self.get_time_string()}

    async def resume(self):
        async with self._lock:
            self._paused = False
            await temporal_persistence.update_clock(self._clock_id, paused=False)
            return {"resumed": True, "time": self.get_time_string()}

    async def set_time_scale(self, scale: float) -> dict:
        async with self._lock:
            self._time_scale = max(0.1, min(100.0, scale))
            await temporal_persistence.update_clock(self._clock_id, time_scale=self._time_scale)
            return {"time_scale": self._time_scale, "time": self.get_time_string()}

    async def get_state(self) -> dict:
        return {
            "clock_id": self._clock_id,
            "tick_count": self._tick_count,
            "year": self._current_year,
            "day": self._current_day,
            "hour": self._current_hour,
            "time_scale": self._time_scale,
            "paused": self._paused,
            "running": self._running,
            "century": self.get_century(),
            "time_string": self.get_time_string(),
        }


sim_clock = TemporalClock()
