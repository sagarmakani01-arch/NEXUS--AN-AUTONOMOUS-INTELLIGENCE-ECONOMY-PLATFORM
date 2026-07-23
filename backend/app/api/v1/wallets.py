from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.domain.models.user import User
from app.domain.schemas.transaction import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService

router = APIRouter(prefix="/wallets", tags=["Wallets"])


@router.post("/{wallet_id}/transfer", response_model=TransactionResponse)
async def transfer(
    wallet_id: str,
    data: TransactionCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TransactionService(session)
    return await service.create_transaction(wallet_id, data)


@router.get("/transactions", response_model=list[TransactionResponse])
async def list_transactions(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
):
    service = TransactionService(session)
    return await service.list_transactions(skip, limit)
