import json
import asyncio
from typing import Optional

from app.temporal.clock import sim_clock
from app.temporal.history import history_manager
from app.temporal.snapshots import snapshot_manager
from app.temporal.replay import replay_engine
from app.temporal.branching import timeline_manager
from app.temporal.causality import causality_engine
from app.temporal.analytics import historical_analytics
from app.temporal.explorer import historical_explorer
from app.temporal.persistence import temporal_persistence


class TemporalEngine:
    """Main orchestrator for the temporal simulation framework."""

    def __init__(self):
        self._initialized = False
        self._running = False

    async def initialize(self):
        if self._initialized:
            return
        await sim_clock.initialize()
        self._initialized = True

    async def start(self):
        await self.initialize()
        self._running = True

    async def stop(self):
        self._running = False

    async def tick(self, full_world_state: dict = None) -> dict:
        if not self._initialized:
            await self.initialize()

        clock_state = await sim_clock.advance(1)

        if full_world_state:
            should_snap = await snapshot_manager.should_snapshot(clock_state["tick_count"])
            if should_snap:
                await snapshot_manager.capture(
                    clock_id=sim_clock._clock_id,
                    tick=clock_state["tick_count"],
                    year=clock_state["year"],
                    world_state=full_world_state,
                )

        return {
            "clock": clock_state,
            "snapshots": snapshot_manager.get_stats(),
            "replay": replay_engine.get_state(),
            "timeline": timeline_manager.get_state(),
            "causality_pending": causality_engine.get_pending_count(),
        }

    async def record_event(self, event_type: str, title: str, **kwargs) -> dict:
        return await history_manager.record(
            clock_id=sim_clock._clock_id,
            event_type=event_type,
            title=title,
            tick=sim_clock.tick_count,
            year=sim_clock.current_year,
            **kwargs,
        )

    async def query_history(self, **kwargs) -> list[dict]:
        return await history_manager.query(
            clock_id=sim_clock._clock_id,
            **kwargs,
        )

    async def create_snapshot(self, label: str = None, world_state: dict = None) -> dict:
        return await snapshot_manager.capture(
            clock_id=sim_clock._clock_id,
            tick=sim_clock.tick_count,
            year=sim_clock.current_year,
            world_state=world_state or {},
            label=label,
        )

    async def get_snapshots(self, timeline_id: str = None) -> list[dict]:
        return await snapshot_manager.get_all(
            sim_clock._clock_id, timeline_id
        )

    async def start_replay(self, start_tick: int = 0, end_tick: int = None, speed: float = 1.0, timeline_id: str = None) -> dict:
        return await replay_engine.start_replay(
            clock_id=sim_clock._clock_id,
            start_tick=start_tick,
            end_tick=end_tick,
            speed=speed,
            timeline_id=timeline_id,
        )

    async def stop_replay(self) -> dict:
        return await replay_engine.stop()

    async def create_branch(self, name: str, description: str = None, branch_point_tick: int = None, divergence_cause: str = None) -> dict:
        return await timeline_manager.create_branch(
            clock_id=sim_clock._clock_id,
            name=name,
            description=description,
            branch_point_tick=branch_point_tick,
            divergence_cause=divergence_cause,
        )

    async def compare_branches(self, branch_a: str, branch_b: str) -> dict:
        return await timeline_manager.compare_branches(
            branch_a_id=branch_a,
            branch_b_id=branch_b,
            clock_id=sim_clock._clock_id,
        )

    async def get_branch_tree(self) -> dict:
        return await timeline_manager.get_branch_tree(sim_clock._clock_id)

    async def record_causality(self, source_id: str, target_id: str, relationship: str, strength: float = 0.5, description: str = None) -> dict:
        return await causality_engine.record_cause(
            source_event_id=source_id,
            target_event_id=target_id,
            relationship_type=relationship,
            strength=strength,
            description=description,
        )

    async def get_causal_chain(self, event_id: str, depth: int = 5) -> dict:
        return await causality_engine.get_causal_chain(event_id, depth)

    async def search_history(self, **kwargs) -> list[dict]:
        return await historical_explorer.search(
            clock_id=sim_clock._clock_id,
            **kwargs,
        )

    async def get_analytics(self) -> dict:
        timeline_summary = await historical_analytics.timeline_summary(sim_clock._clock_id)
        event_dist = await historical_analytics.event_type_distribution(sim_clock._clock_id)
        milestones = await historical_analytics.milestone_detection(sim_clock._clock_id)
        return {
            "summary": timeline_summary,
            "event_distribution": event_dist,
            "milestones": milestones,
        }

    async def get_full_state(self) -> dict:
        clock_state = await sim_clock.get_state()
        snapshot_stats = snapshot_manager.get_stats()
        replay_state = replay_engine.get_state()
        timeline_state = timeline_manager.get_state()
        event_count = await history_manager.get_total_events(sim_clock._clock_id)

        branches = await timeline_manager.list_branches()

        return {
            "clock": clock_state,
            "events": {"total": event_count},
            "snapshots": snapshot_stats,
            "replay": replay_state,
            "timeline": timeline_state,
            "branches": branches,
            "causality": {"pending_edges": causality_engine.get_pending_count()},
            "initialized": self._initialized,
            "running": self._running,
        }

    async def pause(self) -> dict:
        return await sim_clock.pause()

    async def resume(self) -> dict:
        return await sim_clock.resume()

    async def advance_time(self, ticks: int = 1) -> dict:
        return await sim_clock.advance(ticks)

    async def jump_to_year(self, year: int) -> dict:
        return await sim_clock.jump_to_year(year)


temporal_engine = TemporalEngine()
