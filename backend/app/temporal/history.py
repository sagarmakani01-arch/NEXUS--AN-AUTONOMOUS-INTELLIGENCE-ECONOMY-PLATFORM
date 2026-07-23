from typing import Optional

from app.temporal.persistence import temporal_persistence


class HistoryManager:
    """Records and queries historical events across timelines."""

    def __init__(self):
        self._event_buffer: list[dict] = []

    async def record(
        self,
        clock_id: str,
        event_type: str,
        title: str,
        tick: int,
        year: int = None,
        timeline_id: str = None,
        description: str = None,
        location: str = None,
        participants: list = None,
        cause: str = None,
        outcome: str = None,
        impact_score: float = 0.0,
    ) -> dict:
        event = await temporal_persistence.record_event(
            clock_id=clock_id,
            event_type=event_type,
            title=title,
            tick=tick,
            year=year,
            timeline_id=timeline_id,
            description=description,
            location=location,
            participants=participants,
            cause=cause,
            outcome=outcome,
            impact_score=impact_score,
        )

        self._event_buffer.append({
            "id": event.id,
            "type": event_type,
            "title": title,
            "tick": tick,
        })

        if len(self._event_buffer) > 100:
            self._event_buffer = self._event_buffer[-50:]

        return {
            "id": event.id,
            "event_type": event_type,
            "title": title,
            "tick": tick,
        }

    async def query(
        self,
        clock_id: str,
        timeline_id: str = None,
        event_type: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        events = await temporal_persistence.get_events(
            clock_id=clock_id,
            timeline_id=timeline_id,
            event_type=event_type,
            limit=limit,
            offset=offset,
        )
        return [
            {
                "id": e.id,
                "event_type": e.event_type,
                "title": e.title,
                "description": e.description,
                "location": e.location,
                "participants": e.participants,
                "cause": e.cause,
                "outcome": e.outcome,
                "impact_score": e.impact_score,
                "tick": e.tick_occurred,
                "year": e.year_occurred,
            }
            for e in events
        ]

    async def query_in_range(
        self,
        clock_id: str,
        start_tick: int,
        end_tick: int,
        timeline_id: str = None,
    ) -> list[dict]:
        events = await temporal_persistence.get_events_in_range(
            clock_id=clock_id,
            start_tick=start_tick,
            end_tick=end_tick,
            timeline_id=timeline_id,
        )
        return [
            {
                "id": e.id,
                "event_type": e.event_type,
                "title": e.title,
                "tick": e.tick_occurred,
                "year": e.year_occurred,
                "impact_score": e.impact_score,
            }
            for e in events
        ]

    async def get_total_events(self, clock_id: str, timeline_id: str = None) -> int:
        return await temporal_persistence.count_events(clock_id, timeline_id)

    async def get_recent_events(self, clock_id: str, count: int = 10) -> list[dict]:
        return await self.query(clock_id=clock_id, limit=count, offset=0)

    def get_buffer(self) -> list[dict]:
        return list(self._event_buffer)


history_manager = HistoryManager()
