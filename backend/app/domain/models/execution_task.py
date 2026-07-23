import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func

from app.core.database import Base


class ExecutionTask(Base):
    __tablename__ = "execution_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    parent_task_id = Column(String(36), nullable=True)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    required_skills = Column(Text, default="[]")
    status = Column(String(50), default="created")
    priority = Column(String(20), default="medium")
    dependencies = Column(Text, default="[]")
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    estimated_duration = Column(Integer, default=0)
    actual_duration = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    quality_score = Column(Float, nullable=True)
    result = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata_json = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
