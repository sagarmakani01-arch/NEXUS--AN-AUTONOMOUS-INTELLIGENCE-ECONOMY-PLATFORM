from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.domain.models.user import User
from app.domain.schemas.agent import AgentCreate, AgentResponse, AgentUpdate
from app.services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("/", response_model=AgentResponse)
async def create_agent(
    data: AgentCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = AgentService(session)
    return await service.create_agent(user.id, data)


@router.get("/", response_model=list[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 50,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = AgentService(session)
    return await service.list_agents(user.id, skip, limit)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = AgentService(session)
    return await service.get_agent(agent_id)


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    data: AgentUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = AgentService(session)
    return await service.update_agent(agent_id, data)


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = AgentService(session)
    await service.delete_agent(agent_id)
    return {"detail": "Agent deleted"}
