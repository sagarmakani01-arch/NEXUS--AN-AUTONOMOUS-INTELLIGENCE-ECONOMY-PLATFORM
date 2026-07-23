from datetime import datetime

from pydantic import BaseModel, field_validator


class TransactionCreate(BaseModel):
    to_wallet_id: str
    amount: float
    currency: str = "NXC"
    transaction_type: str = "transfer"
    notes: str | None = None


class TransactionResponse(BaseModel):
    id: str
    from_wallet_id: str | None
    to_wallet_id: str | None
    amount: float
    currency: str
    transaction_type: str
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
