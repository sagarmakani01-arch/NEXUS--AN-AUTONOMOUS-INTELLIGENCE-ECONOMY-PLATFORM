from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.marketplace import MarketplaceListing
from app.repositories.base import BaseRepository


class ListingRepository(BaseRepository[MarketplaceListing]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(MarketplaceListing, session)
