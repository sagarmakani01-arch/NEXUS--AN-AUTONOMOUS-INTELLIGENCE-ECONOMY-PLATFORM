from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.wallet import Wallet
from app.repositories.base import BaseRepository


class WalletRepository(BaseRepository[Wallet]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Wallet, session)
