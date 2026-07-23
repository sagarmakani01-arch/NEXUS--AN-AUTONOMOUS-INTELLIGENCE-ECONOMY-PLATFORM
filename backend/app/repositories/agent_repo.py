from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.agent import Agent
from app.repositories.base import BaseRepository


class AgentRepository(BaseRepository[Agent]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Agent, session)

    async def get_by_owner(self, owner_id, skip: int = 0, limit: int = 100):
        result = await self.session.execute(
            select(Agent).where(Agent.owner_id == owner_id).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def get_active_agents(self):
        from sqlalchemy import func

        result = await self.session.execute(
            select(func.count()).select_from(Agent).where(Agent.current_status == "active")
        )
        return result.scalar_one()
