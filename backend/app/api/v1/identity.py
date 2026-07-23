from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from app.simulation.engine import engine

router = APIRouter(prefix="/agents", tags=["agents"])


class AgentProfileResponse(BaseModel):
    id: str
    name: str
    current_status: str
    energy: float
    reputation: float
    wallet_balance: float
    current_goal: str
    identity: dict
    personality: dict
    goal: dict
    skills: list[dict]
    trust_score: float
    memories: list[dict]
    timeline: list[dict]
    relationships: list[dict]


class AgentSearchResult(BaseModel):
    id: str
    name: str
    current_status: str
    energy: float
    reputation: float
    identity: dict
    trust_score: float
    profession: str
    generation: int


@router.get("/search", response_model=list[AgentSearchResult])
async def search_agents(
    q: Optional[str] = Query(None, description="Search by name"),
    profession: Optional[str] = Query(None, description="Filter by profession"),
    status: Optional[str] = Query(None, description="Filter by status (idle, working, resting, searching)"),
    min_reputation: float = Query(0, description="Minimum reputation score"),
    generation: int = Query(0, description="Filter by generation"),
):
    results = engine.search_agents(
        query=q or "",
        profession=profession or "",
        status=status or "",
        min_reputation=min_reputation,
        generation=generation,
    )
    return results


@router.get("/{agent_id}", response_model=AgentProfileResponse)
async def get_agent_profile(agent_id: str):
    profile = await engine.get_agent_profile(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return profile
