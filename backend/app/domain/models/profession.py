import uuid

from sqlalchemy import Column, DateTime, String, Text, func

from app.core.database import Base


class Profession(Base):
    __tablename__ = "professions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
