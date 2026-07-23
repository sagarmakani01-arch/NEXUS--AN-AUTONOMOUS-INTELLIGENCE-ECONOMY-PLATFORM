from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.repositories.company_repo import CompanyRepository


class CompanyService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CompanyRepository(session)

    async def create_company(self, owner_id: str, data: CompanyCreate) -> CompanyResponse:
        company = await self.repo.create(
            owner_id=owner_id,
            name=data.name,
            description=data.description,
            industry=data.industry,
        )
        return CompanyResponse.model_validate(company)

    async def get_company(self, company_id: str) -> CompanyResponse:
        company = await self.repo.get(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return CompanyResponse.model_validate(company)

    async def list_companies(self, skip: int = 0, limit: int = 50) -> list[CompanyResponse]:
        companies = await self.repo.get_multi(skip, limit)
        return [CompanyResponse.model_validate(c) for c in companies]

    async def update_company(self, company_id: str, data: CompanyUpdate) -> CompanyResponse:
        company = await self.repo.get(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        update_data = data.model_dump(exclude_unset=True)
        updated = await self.repo.update(company_id, **update_data)
        return CompanyResponse.model_validate(updated)

    async def delete_company(self, company_id: str) -> bool:
        company = await self.repo.get(company_id)
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
        return await self.repo.delete(company_id)
