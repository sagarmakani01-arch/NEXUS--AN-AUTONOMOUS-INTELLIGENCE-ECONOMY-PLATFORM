import uuid
from sqlalchemy import Column, DateTime, Float, String, Text, func
from app.core.database import Base


class Reflection(Base):
    __tablename__ = "reflections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False, index=True)
    decision_id = Column(String(36), nullable=True, index=True)
    plan_id = Column(String(36), nullable=True, index=True)
    expected_outcome = Column(Text, nullable=True)
    actual_outcome = Column(Text, nullable=True)
    lessons_learned = Column(Text, default="[]")
    success_rate = Column(Float, default=0.0)
    failure_cause = Column(Text, nullable=True)
    experience_gain = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
