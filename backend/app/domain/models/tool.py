import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text, func

from app.core.database import Base


class Tool(Base):
    __tablename__ = "tools"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    tool_type = Column(String(50), default="utility")
    required_permission = Column(String(50), default="basic")
    cost_per_use = Column(Float, default=0.0)
    input_schema = Column(Text, default="{}")
    output_schema = Column(Text, default="{}")
    status = Column(String(50), default="active")
    total_uses = Column(Float, default=0)
    avg_execution_time = Column(Float, default=0.0)
    success_rate = Column(Float, default=1.0)
    metadata_json = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
