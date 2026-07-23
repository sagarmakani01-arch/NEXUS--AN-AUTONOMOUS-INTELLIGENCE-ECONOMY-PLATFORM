import uuid

from sqlalchemy import Column, DateTime, Float, String, Text, func

from app.core.database import Base


class Personality(Base):
    __tablename__ = "personalities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), unique=True, nullable=False, index=True)
    traits = Column(Text, default="{}")
    curiosity = Column(Float, default=50.0)
    creativity = Column(Float, default=50.0)
    reliability = Column(Float, default=50.0)
    risk_tolerance = Column(Float, default=50.0)
    patience = Column(Float, default=50.0)
    leadership = Column(Float, default=50.0)
    cooperation = Column(Float, default=50.0)
    learning_speed = Column(Float, default=50.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
