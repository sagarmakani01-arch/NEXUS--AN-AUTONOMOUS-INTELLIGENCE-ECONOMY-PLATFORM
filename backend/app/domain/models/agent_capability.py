import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func

from app.core.database import Base


class AgentCapability(Base):
    __tablename__ = "agent_capabilities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    skill_name = Column(String(255), nullable=False)
    level = Column(String(50), default="beginner")
    proficiency = Column(Float, default=0.0)
    experience = Column(Float, default=0.0)
    projects_completed = Column(Float, default=0)
    success_rate = Column(Float, default=1.0)
    last_used = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
