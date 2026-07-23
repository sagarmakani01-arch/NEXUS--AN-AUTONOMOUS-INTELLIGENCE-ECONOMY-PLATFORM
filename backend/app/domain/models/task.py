import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    posted_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    required_skills = Column(Text, default="[]")
    reward = Column(Integer, default=0)
    status = Column(String(50), default="open")
    priority = Column(String(20), default="medium")
    deadline = Column(DateTime(timezone=True), nullable=True)
    result = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    poster = relationship("User", backref="posted_tasks")
    agents_list = relationship("Agent", back_populates="tasks", secondary="agent_tasks")
