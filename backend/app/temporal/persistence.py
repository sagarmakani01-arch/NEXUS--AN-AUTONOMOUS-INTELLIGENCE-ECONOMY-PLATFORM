import json
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory as AsyncSessionLocal
from app.domain.models.temporal import (
    TemporalClock,
    HistoricalEvent,
    WorldSnapshot,
    Timeline,
    CausalEdge,
    HistoricalAnalytics,
)


class TemporalPersistence:
    @staticmethod
    async def create_clock(name: str, time_scale: float = 1.0) -> TemporalClock:
        async with AsyncSessionLocal() as session:
            clock = TemporalClock(name=name, time_scale=time_scale)
            session.add(clock)
            await session.commit()
            await session.refresh(clock)
            return clock

    @staticmethod
    async def get_clock(clock_id: str) -> Optional[TemporalClock]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(TemporalClock).where(TemporalClock.id == clock_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_active_clock() -> Optional[TemporalClock]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(TemporalClock).where(TemporalClock.status == "running").order_by(TemporalClock.created_at.desc())
            )
            return result.scalar_one_or_none()

    @staticmethod
    async def update_clock(clock_id: str, **kwargs) -> Optional[TemporalClock]:
        async with AsyncSessionLocal() as session:
            clock = await session.get(TemporalClock, clock_id)
            if not clock:
                return None
            for key, value in kwargs.items():
                setattr(clock, key, value)
            await session.commit()
            await session.refresh(clock)
            return clock

    @staticmethod
    async def record_event(
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
    ) -> HistoricalEvent:
        async with AsyncSessionLocal() as session:
            event = HistoricalEvent(
                clock_id=clock_id,
                timeline_id=timeline_id,
                event_type=event_type,
                title=title,
                description=description,
                location=location,
                participants=json.dumps(participants or []),
                cause=cause,
                outcome=outcome,
                impact_score=impact_score,
                tick_occurred=tick,
                year_occurred=year,
            )
            session.add(event)
            await session.commit()
            await session.refresh(event)
            return event

    @staticmethod
    async def get_events(
        clock_id: str,
        timeline_id: str = None,
        event_type: str = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[HistoricalEvent]:
        async with AsyncSessionLocal() as session:
            query = select(HistoricalEvent).where(HistoricalEvent.clock_id == clock_id)
            if timeline_id:
                query = query.where(HistoricalEvent.timeline_id == timeline_id)
            if event_type:
                query = query.where(HistoricalEvent.event_type == event_type)
            query = query.order_by(HistoricalEvent.tick_occurred).offset(offset).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def get_events_in_range(
        clock_id: str,
        start_tick: int,
        end_tick: int,
        timeline_id: str = None,
    ) -> list[HistoricalEvent]:
        async with AsyncSessionLocal() as session:
            query = (
                select(HistoricalEvent)
                .where(
                    HistoricalEvent.clock_id == clock_id,
                    HistoricalEvent.tick_occurred >= start_tick,
                    HistoricalEvent.tick_occurred <= end_tick,
                )
            )
            if timeline_id:
                query = query.where(HistoricalEvent.timeline_id == timeline_id)
            query = query.order_by(HistoricalEvent.tick_occurred)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def count_events(clock_id: str, timeline_id: str = None) -> int:
        async with AsyncSessionLocal() as session:
            query = select(func.count()).select_from(HistoricalEvent).where(HistoricalEvent.clock_id == clock_id)
            if timeline_id:
                query = query.where(HistoricalEvent.timeline_id == timeline_id)
            result = await session.execute(query)
            return result.scalar() or 0

    @staticmethod
    async def create_snapshot(
        clock_id: str,
        tick: int,
        year: int,
        full_state: dict,
        label: str = None,
        timeline_id: str = None,
    ) -> WorldSnapshot:
        async with AsyncSessionLocal() as session:
            snapshot = WorldSnapshot(
                clock_id=clock_id,
                timeline_id=timeline_id,
                label=label or f"Snapshot at tick {tick}",
                tick=tick,
                year=year,
                full_state=json.dumps(full_state),
                population_state=json.dumps(full_state.get("population", {})),
                economy_state=json.dumps(full_state.get("economy", {})),
                technology_state=json.dumps(full_state.get("technology", {})),
                government_state=json.dumps(full_state.get("government", {})),
                resources_state=json.dumps(full_state.get("resources", {})),
                environment_state=json.dumps(full_state.get("environment", {})),
            )
            session.add(snapshot)
            await session.commit()
            await session.refresh(snapshot)
            return snapshot

    @staticmethod
    async def get_snapshots(
        clock_id: str, timeline_id: str = None, limit: int = 50
    ) -> list[WorldSnapshot]:
        async with AsyncSessionLocal() as session:
            query = select(WorldSnapshot).where(WorldSnapshot.clock_id == clock_id)
            if timeline_id:
                query = query.where(WorldSnapshot.timeline_id == timeline_id)
            query = query.order_by(WorldSnapshot.tick).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def get_snapshot(snapshot_id: str) -> Optional[WorldSnapshot]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(WorldSnapshot).where(WorldSnapshot.id == snapshot_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_closest_snapshot(
        clock_id: str, tick: int, timeline_id: str = None
    ) -> Optional[WorldSnapshot]:
        async with AsyncSessionLocal() as session:
            query = select(WorldSnapshot).where(
                WorldSnapshot.clock_id == clock_id,
                WorldSnapshot.tick <= tick,
            )
            if timeline_id:
                query = query.where(WorldSnapshot.timeline_id == timeline_id)
            query = query.order_by(WorldSnapshot.tick.desc()).limit(1)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @staticmethod
    async def create_timeline(
        name: str,
        description: str = None,
        parent_timeline_id: str = None,
        branch_point_tick: int = None,
        branch_point_year: int = None,
        divergence_cause: str = None,
    ) -> Timeline:
        async with AsyncSessionLocal() as session:
            timeline = Timeline(
                name=name,
                description=description,
                parent_timeline_id=parent_timeline_id,
                branch_point_tick=branch_point_tick,
                branch_point_year=branch_point_year,
                divergence_cause=divergence_cause,
            )
            session.add(timeline)
            await session.commit()
            await session.refresh(timeline)
            return timeline

    @staticmethod
    async def get_timeline(timeline_id: str) -> Optional[Timeline]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(Timeline).where(Timeline.id == timeline_id))
            return result.scalar_one_or_none()

    @staticmethod
    async def get_timelines(timeline_id: str = None) -> list[Timeline]:
        async with AsyncSessionLocal() as session:
            query = select(Timeline)
            if timeline_id:
                query = query.where(Timeline.parent_timeline_id == timeline_id)
            query = query.order_by(Timeline.created_at)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def create_causal_edge(
        source_event_id: str,
        target_event_id: str,
        relationship_type: str,
        strength: float = 0.5,
        description: str = None,
    ) -> CausalEdge:
        async with AsyncSessionLocal() as session:
            edge = CausalEdge(
                source_event_id=source_event_id,
                target_event_id=target_event_id,
                relationship_type=relationship_type,
                strength=strength,
                description=description,
            )
            session.add(edge)
            await session.commit()
            await session.refresh(edge)
            return edge

    @staticmethod
    async def get_causal_edges(event_id: str) -> list[CausalEdge]:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(CausalEdge).where(
                    (CausalEdge.source_event_id == event_id) | (CausalEdge.target_event_id == event_id)
                )
            )
            return list(result.scalars().all())

    @staticmethod
    async def get_causal_chain(event_id: str, depth: int = 5) -> list[CausalEdge]:
        async with AsyncSessionLocal() as session:
            edges = []
            visited = set()
            queue = [event_id]

            for _ in range(depth):
                if not queue:
                    break
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                result = await session.execute(
                    select(CausalEdge).where(CausalEdge.source_event_id == current)
                )
                found = list(result.scalars().all())
                edges.extend(found)
                queue.extend([e.target_event_id for e in found])

            return edges

    @staticmethod
    async def save_analytics(
        analytics_type: str,
        title: str,
        data: dict,
        timeline_id: str = None,
        description: str = None,
    ) -> HistoricalAnalytics:
        async with AsyncSessionLocal() as session:
            analytics = HistoricalAnalytics(
                timeline_id=timeline_id,
                analytics_type=analytics_type,
                title=title,
                description=description,
                data=json.dumps(data),
            )
            session.add(analytics)
            await session.commit()
            await session.refresh(analytics)
            return analytics


temporal_persistence = TemporalPersistence()
