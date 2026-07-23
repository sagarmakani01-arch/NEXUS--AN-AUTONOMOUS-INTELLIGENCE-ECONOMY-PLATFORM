import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="planning")
    priority = Column(String(20), default="medium")
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    estimated_cost = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    quality_score = Column(Float, nullable=True)
    metadata_json = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
