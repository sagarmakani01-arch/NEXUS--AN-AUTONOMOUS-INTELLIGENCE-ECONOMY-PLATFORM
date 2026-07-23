from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import Event, EventType, dispatch
from app.domain.schemas.marketplace import ListingCreate, ListingResponse, ListingUpdate
from app.repositories.listing_repo import ListingRepository


class ListingService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ListingRepository(session)

    async def create_listing(self, seller_agent_id: str, data: ListingCreate) -> ListingResponse:
        import json

        listing = await self.repo.create(
            seller_agent_id=seller_agent_id,
            title=data.title,
            description=data.description,
            listing_type=data.listing_type,
            price=data.price,
            required_skills=json.dumps(data.required_skills),
        )
        await dispatch(Event(EventType.LISTING_CREATED, {"listing_id": listing.id}))
        return ListingResponse.model_validate(listing)

    async def get_listing(self, listing_id: str) -> ListingResponse:
        listing = await self.repo.get(listing_id)
        if not listing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
        return ListingResponse.model_validate(listing)

    async def list_listings(self, skip: int = 0, limit: int = 50) -> list[ListingResponse]:
        listings = await self.repo.get_multi(skip, limit)
        return [ListingResponse.model_validate(l) for l in listings]

    async def update_listing(self, listing_id: str, data: ListingUpdate) -> ListingResponse:
        listing = await self.repo.get(listing_id)
        if not listing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
        update_data = data.model_dump(exclude_unset=True)
        updated = await self.repo.update(listing_id, **update_data)
        return ListingResponse.model_validate(updated)

    async def delete_listing(self, listing_id: str) -> bool:
        listing = await self.repo.get(listing_id)
        if not listing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
        return await self.repo.delete(listing_id)
