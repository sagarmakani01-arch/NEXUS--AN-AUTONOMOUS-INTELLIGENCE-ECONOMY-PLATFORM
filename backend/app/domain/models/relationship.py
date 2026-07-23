import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, func

from app.core.database import Base


class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_a_id = Column(String(36), nullable=False, index=True)
    agent_b_id = Column(String(36), nullable=False, index=True)
    trust = Column(Float, default=50.0)
    respect = Column(Float, default=50.0)
    collaboration_count = Column(Integer, default=0)
    conflict_count = Column(Integer, default=0)
    strength = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction = Column(DateTime(timezone=True), nullable=True)
