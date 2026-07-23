import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func

from app.core.database import Base


class ExecutionResult(Base):
    __tablename__ = "execution_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey("execution_tasks.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    status = Column(String(50), nullable=False)
    quality_score = Column(Float, default=0.0)
    requirements_met = Column(Float, default=0.0)
    errors_count = Column(Float, default=0)
    efficiency_score = Column(Float, default=0.0)
    user_satisfaction = Column(Float, default=0.0)
    deliverables = Column(Text, default="[]")
    feedback = Column(Text, nullable=True)
    lessons_learned = Column(Text, default="[]")
    tools_used = Column(Text, default="[]")
    duration_seconds = Column(Float, default=0)
    cost_incurred = Column(Float, default=0)
    metadata_json = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
