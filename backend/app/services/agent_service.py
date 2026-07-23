from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import Event, EventType, dispatch
from app.domain.schemas.agent import AgentCreate, AgentDetailResponse, AgentResponse, AgentUpdate
from app.repositories.agent_repo import AgentRepository
from app.repositories.wallet_repo import WalletRepository


class AgentService:
    def __init__(self, session: AsyncSession) -> None:
        self.agent_repo = AgentRepository(session)
        self.wallet_repo = WalletRepository(session)
        self.session = session

    async def create_agent(self, owner_id: str, data: AgentCreate) -> AgentResponse:
        agent = await self.agent_repo.create(
            owner_id=owner_id,
            name=data.name,
            profession_id=str(data.profession_id) if data.profession_id else None,
            personality_profile=str(data.personality_profile) if data.personality_profile else "{}",
            current_goal=data.current_goal,
        )
        wallet = await self.wallet_repo.create(agent_id=agent.id, balance=0.0, currency="NXC")

        await dispatch(Event(EventType.AGENT_CREATED, {"agent_id": agent.id, "name": agent.name}))
        await dispatch(Event(EventType.WALLET_CREATED, {"wallet_id": wallet.id, "agent_id": agent.id}))

        return AgentResponse.model_validate(agent)

    async def get_agent(self, agent_id: str) -> AgentDetailResponse:
        agent = await self.agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return AgentDetailResponse.model_validate(agent)

    async def list_agents(self, owner_id: str | None = None, skip: int = 0, limit: int = 50) -> list[AgentResponse]:
        if owner_id:
            agents = await self.agent_repo.get_by_owner(owner_id, skip, limit)
        else:
            agents = await self.agent_repo.get_multi(skip, limit)
        return [AgentResponse.model_validate(a) for a in agents]

    async def update_agent(self, agent_id: str, data: AgentUpdate) -> AgentResponse:
        agent = await self.agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

        update_data = data.model_dump(exclude_unset=True)
        if "profession_id" in update_data and update_data["profession_id"] is not None:
            update_data["profession_id"] = str(update_data["profession_id"])
        if "personality_profile" in update_data and update_data["personality_profile"] is not None:
            update_data["personality_profile"] = str(update_data["personality_profile"])
        updated = await self.agent_repo.update(agent_id, **update_data)

        await dispatch(Event(EventType.AGENT_UPDATED, {"agent_id": agent_id, "changes": update_data}))

        return AgentResponse.model_validate(updated)

    async def delete_agent(self, agent_id: str) -> bool:
        agent = await self.agent_repo.get(agent_id)
        if not agent:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
        return await self.agent_repo.delete(agent_id)

    async def count_agents(self) -> int:
        return await self.agent_repo.count()

    async def count_active_agents(self) -> int:
        return await self.agent_repo.get_active_agents()
