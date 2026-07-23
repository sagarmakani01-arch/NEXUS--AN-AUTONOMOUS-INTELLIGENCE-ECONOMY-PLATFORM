from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.skill import Skill
from app.repositories.base import BaseRepository


class SkillRepository(BaseRepository[Skill]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Skill, session)
