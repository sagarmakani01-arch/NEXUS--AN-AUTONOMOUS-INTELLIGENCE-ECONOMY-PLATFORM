from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.task import Task
from app.repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Task, session)

    async def get_by_status(self, status: str):
        from sqlalchemy import select

        result = await self.session.execute(select(Task).where(Task.status == status))
        return result.scalars().all()
