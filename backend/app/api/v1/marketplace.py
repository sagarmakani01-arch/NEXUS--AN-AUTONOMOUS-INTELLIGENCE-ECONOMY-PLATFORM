from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.domain.models.user import User
from app.marketplace import (
    bidding_engine,
    contract_manager,
    matching_engine,
    marketplace_engine,
    negotiation_engine,
    task_manager,
)
from app.marketplace.persistence import get_marketplace_stats

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


class TaskCreateRequest(BaseModel):
    title: str
    description: str = ""
    required_skills: list[str] = []
    reward: float = 0
    priority: str = "medium"
    deadline: str | None = None


class ProposalRequest(BaseModel):
    task_id: str
    agent_id: str
    proposed_reward: float
    cover_letter: str = ""
    estimated_duration: str = ""


class NegotiateRequest(BaseModel):
    proposal_id: str
    agent_id: str


class ContractActionRequest(BaseModel):
    contract_id: str
    result: str = ""
    rating: float = 5.0
    feedback: str = ""


class CounterRequest(BaseModel):
    proposal_id: str
    counter_reward: float
    message: str = ""


@router.get("/stats")
async def marketplace_stats():
    return await marketplace_engine.get_full_state()


@router.get("/tasks")
async def list_tasks(status: str = "", priority: str = "", skip: int = 0, limit: int = 50):
    return await task_manager.list_tasks(status=status, priority=priority, skip=skip, limit=limit)


@router.get("/tasks/search")
async def search_tasks(query: str = "", min_reward: float = 0):
    return await task_manager.search_tasks(query=query, min_reward=min_reward)


@router.post("/tasks")
async def create_task(data: TaskCreateRequest, user: User = Depends(get_current_user)):
    return await marketplace_engine.create_task_from_poster(
        poster_id=user.id, title=data.title, description=data.description,
        required_skills=data.required_skills, reward=data.reward,
        priority=data.priority, deadline=data.deadline,
    )


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    task = await task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks/{task_id}/proposals")
async def get_task_proposals(task_id: str):
    return await bidding_engine.get_task_bids(task_id)


@router.post("/proposals")
async def submit_proposal(data: ProposalRequest):
    result = await marketplace_engine.submit_proposal(
        task_id=data.task_id, agent_id=data.agent_id,
        proposed_reward=data.proposed_reward,
        cover_letter=data.cover_letter, estimated_duration=data.estimated_duration,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/proposals/agent/{agent_id}")
async def get_agent_proposals(agent_id: str, status: str = ""):
    return await bidding_engine.get_agent_bids(agent_id, status=status)


@router.post("/proposals/{proposal_id}/accept")
async def accept_proposal(proposal_id: str):
    result = await marketplace_engine.accept_proposal_and_create_contract(proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str):
    result = await bidding_engine.reject_proposal(proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/proposals/{proposal_id}/counter")
async def counter_proposal(proposal_id: str, data: CounterRequest):
    result = await bidding_engine.counter_proposal(
        proposal_id, data.counter_reward, data.message,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/proposals/{proposal_id}/accept-counter")
async def accept_counter(proposal_id: str):
    result = await bidding_engine.accept_counter(proposal_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/proposals/{proposal_id}/negotiate")
async def negotiate(proposal_id: str, data: NegotiateRequest):
    from app.simulation.engine import engine as sim_engine
    profile = sim_engine.profiles.get(data.agent_id)
    personality = profile.personality if profile else None
    result = await negotiation_engine.negotiate(proposal_id, data.agent_id, personality)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/matching/{agent_id}")
async def find_opportunities(agent_id: str, limit: int = 10):
    from app.simulation.engine import engine as sim_engine
    profile = sim_engine.profiles.get(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Agent not found in simulation")
    agent_skills = [s.get("skill_name", "") for s in profile.skills]
    return await matching_engine.find_opportunities(
        agent_skills, profile.agent.reputation, profile.agent.energy, limit,
    )


@router.get("/contracts")
async def list_contracts(agent_id: str = "", status: str = ""):
    if agent_id:
        return await contract_manager.list_agent_contracts(agent_id, status)
    return []


@router.get("/contracts/{contract_id}")
async def get_contract(contract_id: str):
    contract = await contract_manager.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.post("/contracts/{contract_id}/accept")
async def accept_contract(contract_id: str):
    result = await contract_manager.accept_contract(contract_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/contracts/{contract_id}/start")
async def start_contract(contract_id: str):
    result = await contract_manager.start_contract(contract_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/contracts/{contract_id}/complete")
async def complete_contract(contract_id: str, data: ContractActionRequest):
    result = await marketplace_engine.complete_contract(
        contract_id, result=data.result, rating=data.rating, feedback=data.feedback,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/contracts/{contract_id}/fail")
async def fail_contract(contract_id: str, reason: str = ""):
    result = await contract_manager.fail_contract(contract_id, reason)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/contracts/stats/{agent_id}")
async def contract_stats(agent_id: str):
    return await contract_manager.get_contract_stats(agent_id)


@router.post("/auto-bid/{agent_id}")
async def auto_bid(agent_id: str):
    from app.simulation.engine import engine as sim_engine
    profile = sim_engine.profiles.get(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Agent not found in simulation")
    agent_skills = [s.get("skill_name", "") for s in profile.skills]
    return await bidding_engine.auto_bid(agent_id, agent_skills, profile.agent.reputation)
