import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Market(Base):
    __tablename__ = "markets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    market_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    current_price = Column(Float, default=0.0)
    base_price = Column(Float, default=0.0)
    supply = Column(Integer, default=0)
    demand = Column(Integer, default=0)
    volume = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)
    volatility = Column(Float, default=0.0)
    status = Column(String(20), default="active")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    market_id = Column(String(36), nullable=False, index=True)
    price = Column(Float, nullable=False)
    supply = Column(Integer, default=0)
    demand = Column(Integer, default=0)
    volume = Column(Integer, default=0)
    change_pct = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class Investment(Base):
    __tablename__ = "investments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    investor_id = Column(String(36), nullable=False, index=True)
    investor_type = Column(String(20), nullable=False, default="agent")
    target_id = Column(String(36), nullable=False, index=True)
    target_type = Column(String(20), nullable=False, default="company")
    amount = Column(Float, nullable=False)
    expected_return_pct = Column(Float, default=0.0)
    actual_return = Column(Float, default=0.0)
    risk_level = Column(String(20), default="medium")
    status = Column(String(20), default="active")
    invested_at = Column(DateTime(timezone=True), server_default=func.now())
    matured_at = Column(DateTime(timezone=True), nullable=True)


class Loan(Base):
    __tablename__ = "loans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    borrower_id = Column(String(36), nullable=False, index=True)
    borrower_type = Column(String(20), nullable=False, default="agent")
    lender_id = Column(String(36), nullable=False, default="bank")
    amount = Column(Float, nullable=False)
    interest_rate = Column(Float, default=0.05)
    term_days = Column(Integer, default=30)
    amount_paid = Column(Float, default=0.0)
    status = Column(String(20), default="active")
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    due_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class EconomicIndicator(Base):
    __tablename__ = "economic_indicators"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    indicator_type = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)
    change_pct = Column(Float, default=0.0)
    period = Column(String(20), default="daily")
    metadata_json = Column(Text, default="{}")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class EconomicEvent(Base):
    __tablename__ = "economic_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), default="medium")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    affected_markets = Column(Text, default="[]")
    affected_sectors = Column(Text, default="[]")
    impact_magnitude = Column(Float, default=0.0)
    status = Column(String(20), default="active")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
