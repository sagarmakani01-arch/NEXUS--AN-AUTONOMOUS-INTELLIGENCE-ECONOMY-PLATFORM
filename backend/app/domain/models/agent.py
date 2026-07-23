import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    profession_id = Column(String(36), ForeignKey("professions.id"), nullable=True)
    personality_profile = Column(Text, default="{}")
    reputation = Column(Float, default=0.0)
    current_goal = Column(Text, nullable=True)
    current_status = Column(String(50), default="idle")
    energy = Column(Integer, default=100)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", backref="agents")
    profession = relationship("Profession", backref="agents")
    wallet = relationship("Wallet", back_populates="agent", uselist=False)
    skills = relationship("Skill", back_populates="agents_list", secondary="agent_skills")
    memories = relationship("Memory", back_populates="agent")
    tasks = relationship("Task", back_populates="agents_list", secondary="agent_tasks")
