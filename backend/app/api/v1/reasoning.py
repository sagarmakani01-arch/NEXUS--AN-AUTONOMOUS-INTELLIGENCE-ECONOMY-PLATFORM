from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.reasoning.engine import reasoning_engine

router = APIRouter(prefix="/reasoning", tags=["reasoning"])


class ReasonRequest(BaseModel):
    agent_id: str
    trigger_type: str
    context: dict | None = None
    priority: int = 5


class ReasonResponse(BaseModel):
    decision_id: str | None = None
    decision: str
    reasoning_summary: str
    confidence: float
    expected_outcome: str
    risk_level: str
    estimated_cost: float
    estimated_reward: float
    next_goal: str
    alternative_options: list[str]
    provider_used: str
    reasoning_duration_ms: float
    status: str


class ReflectRequest(BaseModel):
    agent_id: str
    decision_id: str
    expected_outcome: str
    actual_outcome: str
    success: bool
    cost: float = 0
    reward: float = 0


class CreatePlanRequest(BaseModel):
    agent_id: str
    goal: str
    decision_id: str = ""


@router.post("/reason", response_model=ReasonResponse)
async def reason(request: ReasonRequest):
    result = await reasoning_engine.reason(
        agent_id=request.agent_id,
        trigger_type=request.trigger_type,
        context_data=request.context,
    )
    if "error" in result and not result.get("decision"):
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.get("/decisions")
async def get_decisions(
    agent_id: str = Query(..., description="Agent ID"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    decisions = await reasoning_engine.get_decisions(agent_id, limit, offset)
    return {"decisions": decisions, "total": len(decisions)}


@router.get("/decisions/{decision_id}")
async def get_decision(decision_id: str, agent_id: str = Query(...)):
    decision = await reasoning_engine._decision_store.get(decision_id)
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    if decision["agent_id"] != agent_id:
        raise HTTPException(status_code=403, detail="Access denied")
    return decision


@router.get("/decisions/search")
async def search_decisions(
    agent_id: str = Query(...),
    q: str = Query(..., min_length=1),
):
    results = await reasoning_engine.search_decisions(agent_id, q)
    return {"results": results, "count": len(results)}


@router.get("/plans")
async def get_plans(agent_id: str = Query(...)):
    plans = await reasoning_engine.get_plans(agent_id)
    return {"plans": plans}


@router.post("/plans")
async def create_plan(request: CreatePlanRequest):
    plan = await reasoning_engine.create_plan(
        agent_id=request.agent_id,
        goal=request.goal,
        decision_id=request.decision_id,
    )
    return plan


@router.post("/plans/advance")
async def advance_plan(agent_id: str = Query(...)):
    plan = await reasoning_engine.advance_plan(agent_id)
    if not plan:
        raise HTTPException(status_code=404, detail="No active plan")
    return plan


@router.get("/reflection")
async def get_reflections(
    agent_id: str = Query(...),
    limit: int = Query(20, ge=1, le=100),
):
    reflections = await reasoning_engine.get_reflections(agent_id, limit)
    return {"reflections": reflections, "total": len(reflections)}


@router.post("/reflection")
async def create_reflection(request: ReflectRequest):
    result = await reasoning_engine.reflect(
        agent_id=request.agent_id,
        decision_id=request.decision_id,
        expected_outcome=request.expected_outcome,
        actual_outcome=request.actual_outcome,
        success=request.success,
        cost=request.cost,
        reward=request.reward,
    )
    return result


@router.get("/reasoning-history")
async def get_reasoning_history(
    agent_id: str = Query(...),
    limit: int = Query(30, ge=1, le=100),
):
    return await reasoning_engine.get_reasoning_history(agent_id, limit)


@router.post("/replay")
async def replay_decision(
    agent_id: str = Query(...),
    decision_id: str = Query(...),
):
    result = await reasoning_engine.replay(agent_id, decision_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/state")
async def get_reasoning_state():
    return reasoning_engine.get_full_state()


@router.get("/agent/{agent_id}")
async def get_agent_reasoning(agent_id: str):
    return reasoning_engine.get_agent_reasoning_state(agent_id)


@router.post("/trigger")
async def trigger_decision(request: ReasonRequest):
    trigger_id = await reasoning_engine.trigger_decision(
        agent_id=request.agent_id,
        trigger_type=request.trigger_type,
        context_data=request.context,
        priority=request.priority,
    )
    if not trigger_id:
        raise HTTPException(status_code=503, detail="Queue full or unavailable")
    return {"trigger_id": trigger_id, "status": "queued"}
