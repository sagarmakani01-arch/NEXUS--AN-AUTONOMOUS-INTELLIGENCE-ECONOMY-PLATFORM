import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func

from app.core.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("tasks.id"), nullable=False)
    proposal_id = Column(String(36), ForeignKey("proposals.id"), nullable=False)
    poster_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    agreed_reward = Column(Float, nullable=False)
    status = Column(String(50), default="created")
    terms = Column(Text, nullable=True)
    result = Column(Text, nullable=True)
    rating = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
