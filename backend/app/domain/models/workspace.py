import uuid

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func

from app.core.database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    files_json = Column("files", Text, default="[]")
    notes = Column(Text, default="")
    artifacts_json = Column("artifacts", Text, default="[]")
    task_history_json = Column("task_history", Text, default="[]")
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
