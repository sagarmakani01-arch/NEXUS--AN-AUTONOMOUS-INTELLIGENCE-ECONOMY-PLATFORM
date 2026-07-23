import uuid

from sqlalchemy import Column, DateTime, String, Text, func

from app.core.database import Base


class EventLog(Base):
    __tablename__ = "event_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    payload = Column(Text, default="{}")
    status = Column(String(50), default="logged")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
