import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False, index=True)
    asset_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    value = Column(Float, default=0.0)
    purchase_price = Column(Float, default=0.0)
    maintenance_cost = Column(Float, default=0.0)
    condition_score = Column(Float, default=100.0)
    quantity = Column(Integer, default=1)
    metadata_json = Column(Text, default="{}")
    status = Column(String(50), default="active")
    acquired_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
