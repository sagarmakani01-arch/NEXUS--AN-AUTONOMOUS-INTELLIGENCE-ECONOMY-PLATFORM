import uuid
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False, index=True)
    decision_id = Column(String(36), nullable=True, index=True)
    goal = Column(String(255), nullable=False)
    status = Column(String(20), default="active")
    milestones = Column(Text, default="[]")
    current_milestone_index = Column(Integer, default=0)
    tasks = Column(Text, default="[]")
    current_task_index = Column(Integer, default=0)
    actions = Column(Text, default="[]")
    current_action_index = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    evaluation = Column(Text, default="{}")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
