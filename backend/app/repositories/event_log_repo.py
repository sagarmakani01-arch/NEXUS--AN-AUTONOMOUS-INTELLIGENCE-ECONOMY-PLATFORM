from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.event_log import EventLog
from app.repositories.base import BaseRepository


class EventLogRepository(BaseRepository[EventLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(EventLog, session)
