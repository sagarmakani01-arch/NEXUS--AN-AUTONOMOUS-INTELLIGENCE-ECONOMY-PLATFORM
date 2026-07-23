import uuid

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Skill(Base):
    __tablename__ = "skills"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    category = Column(String(100), nullable=True)
    description = Column(String(500), nullable=True)
    proficiency_levels = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    agents_list = relationship("Agent", back_populates="skills", secondary="agent_skills")
