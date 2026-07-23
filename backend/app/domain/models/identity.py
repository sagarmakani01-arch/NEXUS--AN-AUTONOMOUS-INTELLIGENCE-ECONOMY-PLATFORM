import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Identity(Base):
    __tablename__ = "identities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), unique=True, nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    display_name = Column(String(120), nullable=False, unique=True)
    generation = Column(Integer, default=1)
    status = Column(String(50), default="active")
    profession = Column(String(100), default="")
    profession_category = Column(String(50), default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
