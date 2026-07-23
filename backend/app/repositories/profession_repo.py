from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.profession import Profession
from app.repositories.base import BaseRepository


class ProfessionRepository(BaseRepository[Profession]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Profession, session)
