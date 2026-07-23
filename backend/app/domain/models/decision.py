import uuid
from sqlalchemy import Column, DateTime, Float, String, Text, func
from app.core.database import Base


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False, index=True)
    trigger_type = Column(String(50), nullable=False)
    trigger_id = Column(String(36), nullable=True)
    decision = Column(String(255), nullable=False)
    reasoning_summary = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5)
    expected_outcome = Column(Text, nullable=True)
    risk_level = Column(String(20), default="medium")
    estimated_cost = Column(Float, default=0.0)
    estimated_reward = Column(Float, default=0.0)
    next_goal = Column(String(255), nullable=True)
    alternative_options = Column(Text, default="[]")
    context_snapshot = Column(Text, default="{}")
    provider_used = Column(String(50), default="deterministic")
    reasoning_duration_ms = Column(Float, default=0.0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
