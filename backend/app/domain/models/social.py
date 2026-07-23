import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class SocialConnection(Base):
    __tablename__ = "social_connections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_a_id = Column(String(36), nullable=False, index=True)
    entity_a_type = Column(String(20), nullable=False, default="agent")
    entity_b_id = Column(String(36), nullable=False, index=True)
    entity_b_type = Column(String(20), nullable=False, default="agent")
    relationship_type = Column(String(30), nullable=False, default="colleague")
    trust_level = Column(Float, default=50.0)
    relationship_strength = Column(Float, default=0.0)
    interaction_count = Column(Integer, default=0)
    shared_knowledge_count = Column(Integer, default=0)
    sentiment_score = Column(Float, default=0.5)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_interaction_at = Column(DateTime(timezone=True), nullable=True)


class Community(Base):
    __tablename__ = "communities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    community_type = Column(String(30), nullable=False, default="open")
    purpose = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    member_count = Column(Integer, default=0)
    knowledge_pool_size = Column(Integer, default=0)
    reputation = Column(Float, default=50.0)
    status = Column(String(20), default="active")
    founded_by = Column(String(36), nullable=True)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class CommunityMember(Base):
    __tablename__ = "community_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id = Column(String(36), nullable=False, index=True)
    member_id = Column(String(36), nullable=False, index=True)
    member_type = Column(String(20), nullable=False, default="agent")
    role = Column(String(30), default="member")
    contribution_score = Column(Float, default=0.0)
    knowledge_shared = Column(Integer, default=0)
    status = Column(String(20), default="active")
    joined_at = Column(DateTime(timezone=True), server_default=func.now())


class TrustRecord(Base):
    __tablename__ = "trust_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_a_id = Column(String(36), nullable=False, index=True)
    entity_a_type = Column(String(20), nullable=False, default="agent")
    entity_b_id = Column(String(36), nullable=False, index=True)
    entity_b_type = Column(String(20), nullable=False, default="agent")
    change_amount = Column(Float, nullable=False)
    reason = Column(String(255), nullable=False)
    interaction_type = Column(String(30), nullable=False)
    previous_trust = Column(Float, nullable=False)
    new_trust = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
