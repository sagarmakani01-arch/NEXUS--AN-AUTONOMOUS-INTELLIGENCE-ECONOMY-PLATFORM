import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, func

from app.core.database import Base


class AgentSkill(Base):
    __tablename__ = "agent_skill_profiles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    max_experience = Column(Integer, default=100)
    learning_progress = Column(Float, default=0.0)
    certified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
