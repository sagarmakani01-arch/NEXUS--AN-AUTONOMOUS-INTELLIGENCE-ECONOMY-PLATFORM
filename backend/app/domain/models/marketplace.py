import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func

from app.core.database import Base


class MarketplaceListing(Base):
    __tablename__ = "marketplace_listings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    seller_agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    listing_type = Column(String(50), default="service")
    price = Column(Float, default=0.0)
    required_skills = Column(Text, default="[]")
    status = Column(String(50), default="active")
    quantity = Column(Integer, default=1)
    metadata_ = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
