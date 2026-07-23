import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class CulturalIdentity(Base):
    __tablename__ = "cultural_identities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    core_values = Column(Text, default="{}")
    shared_history = Column(Text, default="[]")
    social_norms = Column(Text, default="[]")
    historical_symbols = Column(Text, default="[]")
    long_term_goals = Column(Text, default="[]")
    identity_strength = Column(Float, default=50.0)
    last_evolution = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ValueSystem(Base):
    __tablename__ = "value_systems"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, unique=True, index=True)
    innovation = Column(Float, default=50.0)
    cooperation = Column(Float, default=50.0)
    competition = Column(Float, default=50.0)
    education = Column(Float, default=50.0)
    efficiency = Column(Float, default=50.0)
    sustainability = Column(Float, default=50.0)
    exploration = Column(Float, default=50.0)
    security = Column(Float, default=50.0)
    transparency = Column(Float, default=50.0)
    last_shift = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Institution(Base):
    __tablename__ = "cultural_institutions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    institution_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    founding_date = Column(DateTime(timezone=True), server_default=func.now())
    strength = Column(Float, default=50.0)
    influence = Column(Float, default=50.0)
    membership_count = Column(Integer, default=0)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Tradition(Base):
    __tablename__ = "cultural_traditions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(String(50), default="annual")
    last_held = Column(DateTime(timezone=True), nullable=True)
    next_held = Column(DateTime(timezone=True), nullable=True)
    impact_score = Column(Float, default=0.0)
    established_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CivilizationCommunity(Base):
    __tablename__ = "civilization_communities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    community_type = Column(String(50), nullable=False)
    member_count = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CommunityMembership(Base):
    __tablename__ = "community_memberships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id = Column(String(36), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    entity_type = Column(String(20), nullable=False, default="agent")
    role = Column(String(30), default="member")
    contribution_score = Column(Float, default=0.0)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())


class CollectiveMemory(Base):
    __tablename__ = "collective_memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    impact_score = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class SocialDynamics(Base):
    __tablename__ = "social_dynamics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, unique=True, index=True)
    collaboration_score = Column(Float, default=50.0)
    competition_score = Column(Float, default=50.0)
    trust_level = Column(Float, default=50.0)
    influence_distribution = Column(Text, default="{}")
    knowledge_sharing_score = Column(Float, default=50.0)
    community_growth_rate = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ReputationEntry(Base):
    __tablename__ = "reputation_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    entity_id = Column(String(36), nullable=False, index=True)
    entity_type = Column(String(20), nullable=False, default="agent")
    influence_score = Column(Float, default=0.0)
    contribution_count = Column(Integer, default=0)
    sustained_engagement = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CulturalTimeline(Base):
    __tablename__ = "cultural_timelines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    change_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    cause = Column(String(255), nullable=True)
    impact_score = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class CivilizationIdentityScore(Base):
    __tablename__ = "civilization_identity_scores"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, unique=True, index=True)
    knowledge_orientation = Column(Float, default=50.0)
    innovation_orientation = Column(Float, default=50.0)
    economic_stability = Column(Float, default=50.0)
    social_cohesion = Column(Float, default=50.0)
    institutional_strength = Column(Float, default=50.0)
    adaptability = Column(Float, default=50.0)
    last_calculated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
