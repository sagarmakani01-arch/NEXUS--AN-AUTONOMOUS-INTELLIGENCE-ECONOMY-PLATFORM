import uuid

from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.core.database import Base


class AgentMemory(Base):
    __tablename__ = "agent_memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    importance = Column(String(20), default="medium")
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    related_agent_id = Column(String(36), nullable=True)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
