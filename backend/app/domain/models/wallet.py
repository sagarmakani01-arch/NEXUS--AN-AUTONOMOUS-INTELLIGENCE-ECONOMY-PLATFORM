import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), unique=True, nullable=False, index=True)
    balance = Column(Float, default=0.0)
    reserved_balance = Column(Float, default=0.0)
    total_earned = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    lifetime_earnings = Column(Float, default=0.0)
    lifetime_expenses = Column(Float, default=0.0)
    compute_credits = Column(Integer, default=100)
    compute_used = Column(Integer, default=0)
    currency = Column(String(10), default="NXC")
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
