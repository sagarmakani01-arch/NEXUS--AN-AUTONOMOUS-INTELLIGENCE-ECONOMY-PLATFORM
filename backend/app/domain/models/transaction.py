import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func

from app.core.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_wallet_id = Column(String(36), ForeignKey("wallets.id"), nullable=True)
    to_wallet_id = Column(String(36), ForeignKey("wallets.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="NXC")
    transaction_type = Column(String(50), nullable=False)
    status = Column(String(50), default="completed")
    reference_id = Column(String(36), nullable=True)
    reference_type = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    metadata_ = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
