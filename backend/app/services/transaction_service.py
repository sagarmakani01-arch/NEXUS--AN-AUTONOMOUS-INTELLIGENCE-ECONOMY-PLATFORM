from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import Event, EventType, dispatch
from app.domain.schemas.transaction import TransactionCreate, TransactionResponse
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.wallet_repo import WalletRepository


class TransactionService:
    def __init__(self, session: AsyncSession) -> None:
        self.tx_repo = TransactionRepository(session)
        self.wallet_repo = WalletRepository(session)

    async def create_transaction(self, from_wallet_id: str, data: TransactionCreate) -> TransactionResponse:
        from_wallet = await self.wallet_repo.get(from_wallet_id)
        if not from_wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sender wallet not found")

        to_wallet = await self.wallet_repo.get(str(data.to_wallet_id))
        if not to_wallet:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipient wallet not found")

        if from_wallet.balance < data.amount:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient balance")

        from_wallet.balance -= data.amount
        to_wallet.balance += data.amount

        tx = await self.tx_repo.create(
            from_wallet_id=from_wallet_id,
            to_wallet_id=str(data.to_wallet_id),
            amount=data.amount,
            currency=data.currency,
            transaction_type=data.transaction_type,
            notes=data.notes,
        )

        await dispatch(Event(EventType.TRANSACTION_CREATED, {"transaction_id": tx.id, "amount": data.amount}))

        return TransactionResponse.model_validate(tx)

    async def list_transactions(self, skip: int = 0, limit: int = 50) -> list[TransactionResponse]:
        txs = await self.tx_repo.get_multi(skip, limit)
        return [TransactionResponse.model_validate(t) for t in txs]
