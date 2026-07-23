from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import json

from app.temporal.engine import temporal_engine
from app.temporal.clock import sim_clock
from app.temporal.history import history_manager
from app.temporal.snapshots import snapshot_manager
from app.temporal.replay import replay_engine
from app.temporal.branching import timeline_manager
from app.temporal.causality import causality_engine
from app.temporal.analytics import historical_analytics
from app.temporal.explorer import historical_explorer
from app.temporal.persistence import temporal_persistence

router = APIRouter(prefix="/api/v1/temporal", tags=["Temporal"])


class EventRecordRequest(BaseModel):
    event_type: str
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    participants: Optional[list[str]] = None
    cause: Optional[str] = None
    outcome: Optional[str] = None
    impact_score: float = 0.0


class SnapshotRequest(BaseModel):
    label: Optional[str] = None
    world_state: Optional[dict] = None


class BranchCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    branch_point_tick: Optional[int] = None
    divergence_cause: Optional[str] = None


class CausalEdgeRequest(BaseModel):
    source_event_id: str
    target_event_id: str
    relationship_type: str
    strength: float = 0.5
    description: Optional[str] = None


class SearchRequest(BaseModel):
    query: Optional[str] = None
    event_type: Optional[str] = None
    location: Optional[str] = None
    participant: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    timeline_id: Optional[str] = None
    limit: int = 50


class ReplayRequest(BaseModel):
    start_tick: int = 0
    end_tick: Optional[int] = None
    speed: float = 1.0
    timeline_id: Optional[str] = None


# --- Clock endpoints ---

@router.get("/clock")
async def get_clock_state():
    return await temporal_engine.get_full_state()


@router.post("/clock/pause")
async def pause_clock():
    return await temporal_engine.pause()


@router.post("/clock/resume")
async def resume_clock():
    return await temporal_engine.resume()


@router.post("/clock/advance")
async def advance_clock(ticks: int = Query(1, ge=1, le=1000)):
    return await temporal_engine.advance_time(ticks)


@router.post("/clock/jump")
async def jump_clock(year: int = Query(..., ge=2025)):
    return await temporal_engine.jump_to_year(year)


@router.post("/clock/scale")
async def set_time_scale(scale: float = Query(..., ge=0.1, le=100.0)):
    return await sim_clock.set_time_scale(scale)


# --- History endpoints ---

@router.post("/history/record")
async def record_event(request: EventRecordRequest):
    return await temporal_engine.record_event(
        event_type=request.event_type,
        title=request.title,
        description=request.description,
        location=request.location,
        participants=request.participants,
        cause=request.cause,
        outcome=request.outcome,
        impact_score=request.impact_score,
    )


@router.get("/history/events")
async def get_events(
    timeline_id: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = Query(100, ge=1, le=5000),
    offset: int = Query(0, ge=0),
):
    return await temporal_engine.query_history(
        timeline_id=timeline_id,
        event_type=event_type,
        limit=limit,
        offset=offset,
    )


@router.get("/history/events/range")
async def get_events_in_range(
    start_tick: int = Query(..., ge=0),
    end_tick: int = Query(..., ge=0),
    timeline_id: Optional[str] = None,
):
    return await history_manager.query_in_range(
        clock_id=sim_clock._clock_id,
        start_tick=start_tick,
        end_tick=end_tick,
        timeline_id=timeline_id,
    )


@router.get("/history/events/{event_id}")
async def get_event_detail(event_id: str):
    event = await historical_explorer.get_event_detail(event_id, sim_clock._clock_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/history/types")
async def get_event_types(timeline_id: Optional[str] = None):
    return {"types": await historical_explorer.get_event_types(sim_clock._clock_id, timeline_id)}


@router.get("/history/count")
async def get_event_count(timeline_id: Optional[str] = None):
    count = await history_manager.get_total_events(sim_clock._clock_id, timeline_id)
    return {"count": count}


@router.get("/history/recent")
async def get_recent_events(count: int = Query(10, ge=1, le=100)):
    return await history_manager.get_recent_events(sim_clock._clock_id, count)


# --- Snapshot endpoints ---

@router.post("/snapshots/create")
async def create_snapshot(request: SnapshotRequest):
    return await temporal_engine.create_snapshot(
        label=request.label,
        world_state=request.world_state,
    )


@router.get("/snapshots")
async def get_snapshots(timeline_id: Optional[str] = None):
    return await temporal_engine.get_snapshots(timeline_id)


@router.get("/snapshots/{snapshot_id}")
async def get_snapshot(snapshot_id: str):
    snapshot = await snapshot_manager.get_by_id(snapshot_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.get("/snapshots/at/{tick}")
async def get_snapshot_at_tick(tick: int, timeline_id: Optional[str] = None):
    snapshot = await snapshot_manager.get_closest(sim_clock._clock_id, tick, timeline_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found for this tick")
    return snapshot


@router.post("/snapshots/interval")
async def set_snapshot_interval(interval: int = Query(..., ge=10, le=1000)):
    snapshot_manager.set_interval(interval)
    return {"interval": interval}


# --- Replay endpoints ---

@router.post("/replay/start")
async def start_replay(request: ReplayRequest):
    return await temporal_engine.start_replay(
        start_tick=request.start_tick,
        end_tick=request.end_tick,
        speed=request.speed,
        timeline_id=request.timeline_id,
    )


@router.post("/replay/stop")
async def stop_replay():
    return await temporal_engine.stop_replay()


@router.get("/replay/state")
async def get_replay_state():
    return replay_engine.get_state()


@router.post("/replay/speed")
async def set_replay_speed(speed: float = Query(..., ge=0.1, le=10.0)):
    return await replay_engine.set_speed(speed)


@router.post("/replay/step")
async def step_replay(timeline_id: Optional[str] = None):
    result = await replay_engine.step(sim_clock._clock_id, timeline_id)
    if not result:
        raise HTTPException(status_code=400, detail="No replay in progress")
    return result


@router.post("/replay/jump")
async def jump_replay(tick: int = Query(..., ge=0)):
    return await replay_engine.jump_to(tick)


# --- Timeline / Branching endpoints ---

@router.post("/timelines/branch")
async def create_branch(request: BranchCreateRequest):
    return await temporal_engine.create_branch(
        name=request.name,
        description=request.description,
        branch_point_tick=request.branch_point_tick,
        divergence_cause=request.divergence_cause,
    )


@router.get("/timelines")
async def list_branches(parent_id: Optional[str] = None):
    return await timeline_manager.list_branches(parent_id)


@router.get("/timelines/tree")
async def get_branch_tree():
    return await temporal_engine.get_branch_tree()


@router.get("/timelines/{branch_id}")
async def get_branch(branch_id: str):
    branch = await timeline_manager.get_branch(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch


@router.post("/timelines/compare")
async def compare_branches(branch_a: str = Query(...), branch_b: str = Query(...)):
    return await temporal_engine.compare_branches(branch_a, branch_b)


# --- Causality endpoints ---

@router.post("/causality/record")
async def record_causality(request: CausalEdgeRequest):
    return await temporal_engine.record_causality(
        source_id=request.source_event_id,
        target_id=request.target_event_id,
        relationship=request.relationship_type,
        strength=request.strength,
        description=request.description,
    )


@router.get("/causality/effects/{event_id}")
async def get_effects(event_id: str):
    return {"effects": await causality_engine.get_effects(event_id)}


@router.get("/causality/causes/{event_id}")
async def get_causes(event_id: str):
    return {"causes": await causality_engine.get_causes(event_id)}


@router.get("/causality/chain/{event_id}")
async def get_causal_chain(event_id: str, depth: int = Query(5, ge=1, le=20)):
    return await temporal_engine.get_causal_chain(event_id, depth)


@router.get("/causality/cascade/{event_id}")
async def find_cascade(event_id: str, max_depth: int = Query(10, ge=1, le=20)):
    return {"cascade": await causality_engine.find_cascade(event_id, max_depth)}


@router.get("/causality/stats")
async def get_causality_stats():
    return await causality_engine.get_graph_stats(sim_clock._clock_id)


# --- Explorer endpoints ---

@router.post("/explorer/search")
async def search_history(request: SearchRequest):
    return await historical_explorer.search(
        clock_id=sim_clock._clock_id,
        query=request.query,
        event_type=request.event_type,
        location=request.location,
        participant=request.participant,
        start_year=request.start_year,
        end_year=request.end_year,
        timeline_id=request.timeline_id,
        limit=request.limit,
    )


@router.get("/explorer/participant/{name}")
async def by_participant(name: str, timeline_id: Optional[str] = None):
    return await historical_explorer.by_participant(sim_clock._clock_id, name, timeline_id)


@router.get("/explorer/location/{location}")
async def by_location(location: str, timeline_id: Optional[str] = None):
    return await historical_explorer.by_location(sim_clock._clock_id, location, timeline_id)


@router.get("/explorer/type/{event_type}")
async def by_event_type(event_type: str, timeline_id: Optional[str] = None):
    return await historical_explorer.by_event_type(sim_clock._clock_id, event_type, timeline_id)


@router.get("/explorer/timeline/{timeline_id}")
async def get_timeline_events(timeline_id: str):
    return await historical_explorer.get_timeline_events(sim_clock._clock_id, timeline_id)


# --- Analytics endpoints ---

@router.get("/analytics")
async def get_analytics():
    return await temporal_engine.get_analytics()


@router.get("/analytics/influential")
async def influential_events(limit: int = Query(10, ge=1, le=100)):
    return await historical_analytics.most_influential_events(sim_clock._clock_id, limit=limit)


@router.get("/analytics/distribution")
async def event_distribution():
    return await historical_analytics.event_type_distribution(sim_clock._clock_id)


@router.get("/analytics/summary")
async def timeline_summary():
    return await historical_analytics.timeline_summary(sim_clock._clock_id)


@router.get("/analytics/eras")
async def era_analysis():
    return await historical_analytics.era_analysis(sim_clock._clock_id)


@router.get("/analytics/milestones")
async def milestones(threshold: float = Query(0.7, ge=0.0, le=1.0)):
    return await historical_analytics.milestone_detection(sim_clock._clock_id, threshold=threshold)
