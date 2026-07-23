import json
from typing import Optional

from app.temporal.persistence import temporal_persistence


class HistoricalExplorer:
    """Browse history by citizen, company, institution, civilization, technology, region, time."""

    def __init__(self):
        self._search_index: dict[str, list[str]] = {}

    async def search(
        self,
        clock_id: str,
        query: str = None,
        event_type: str = None,
        location: str = None,
        participant: str = None,
        start_year: int = None,
        end_year: int = None,
        timeline_id: str = None,
        limit: int = 50,
    ) -> list[dict]:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=10000
        )

        filtered = []
        for e in events:
            if query and query.lower() not in (e.title or "").lower() and query.lower() not in (e.description or "").lower():
                continue
            if event_type and e.event_type != event_type:
                continue
            if location and (e.location or "").lower() != location.lower():
                continue
            if participant:
                try:
                    p_list = json.loads(e.participants) if isinstance(e.participants, str) else e.participants
                    if isinstance(p_list, list) and participant not in p_list:
                        continue
                except (json.JSONDecodeError, TypeError):
                    continue
            if start_year and (e.year_occurred or 0) < start_year:
                continue
            if end_year and (e.year_occurred or 0) > end_year:
                continue
            filtered.append({
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
            })
            if len(filtered) >= limit:
                break

        return filtered

    async def by_participant(self, clock_id: str, participant_name: str, timeline_id: str = None) -> list[dict]:
        return await self.search(clock_id=clock_id, participant=participant_name, timeline_id=timeline_id)

    async def by_location(self, clock_id: str, location: str, timeline_id: str = None) -> list[dict]:
        return await self.search(clock_id=clock_id, location=location, timeline_id=timeline_id)

    async def by_event_type(self, clock_id: str, event_type: str, timeline_id: str = None) -> list[dict]:
        return await self.search(clock_id=clock_id, event_type=event_type, timeline_id=timeline_id)

    async def by_time_range(
        self, clock_id: str, start_year: int, end_year: int, timeline_id: str = None
    ) -> list[dict]:
        return await self.search(
            clock_id=clock_id, start_year=start_year, end_year=end_year, timeline_id=timeline_id
        )

    async def get_event_detail(self, event_id: str, clock_id: str) -> Optional[dict]:
        events = await temporal_persistence.get_events(clock_id=clock_id, limit=10000)
        for e in events:
            if e.id == event_id:
                return {
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
        return None

    async def get_timeline_events(self, clock_id: str, timeline_id: str = None) -> list[dict]:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=5000
        )
        return [
            {
                "id": e.id,
                "type": e.event_type,
                "title": e.title,
                "year": e.year_occurred,
                "tick": e.tick_occurred,
                "impact": e.impact_score,
            }
            for e in events
        ]

    async def get_event_types(self, clock_id: str, timeline_id: str = None) -> list[str]:
        events = await temporal_persistence.get_events(
            clock_id=clock_id, timeline_id=timeline_id, limit=10000
        )
        types = set(e.event_type for e in events)
        return sorted(types)


historical_explorer = HistoricalExplorer()
