import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Civilization(Base):
    __tablename__ = "civilizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    leader_agent_id = Column(String(36), nullable=True)
    founding_date = Column(DateTime(timezone=True), server_default=func.now())
    population = Column(Integer, default=0)
    territory_size = Column(Float, default=100.0)
    technology_level = Column(Float, default=1.0)
    economic_power = Column(Float, default=50.0)
    military_strength = Column(Float, default=20.0)
    cultural_influence = Column(Float, default=30.0)
    research_output = Column(Float, default=0.0)
    happiness = Column(Float, default=60.0)
    resource_availability = Column(String(50), default="abundant")
    government_type = Column(String(50), default="centralized")
    economic_model = Column(String(50), default="free_market")
    values = Column(Text, default="{}")
    priorities = Column(Text, default="[]")
    achievements = Column(Text, default="[]")
    historical_events = Column(Text, default="[]")
    reputation = Column(Float, default=50.0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CivilizationRules(Base):
    __tablename__ = "civilization_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    economic_model = Column(String(50), default="free_market")
    governance_type = Column(String(50), default="centralized")
    resource_availability = Column(String(50), default="abundant")
    migration_policy = Column(String(50), default="open")
    trade_policy = Column(String(50), default="open")
    research_policy = Column(String(50), default="collaborative")
    defense_policy = Column(String(50), default="defensive")
    custom_rules = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DiplomaticRelation(Base):
    __tablename__ = "diplomatic_relations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_a_id = Column(String(36), nullable=False)
    civilization_b_id = Column(String(36), nullable=False)
    relation_level = Column(Float, default=50.0)
    status = Column(String(50), default="neutral")
    trust_score = Column(Float, default=50.0)
    trade_volume = Column(Float, default=0.0)
    agreements_count = Column(Integer, default=0)
    conflicts_count = Column(Integer, default=0)
    last_interaction = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TradeAgreement(Base):
    __tablename__ = "trade_agreements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_a_id = Column(String(36), nullable=False)
    civilization_b_id = Column(String(36), nullable=False)
    trade_type = Column(String(50), nullable=False)
    resource_offered = Column(String(100), nullable=False)
    resource_requested = Column(String(100), nullable=False)
    amount_offered = Column(Float, default=0.0)
    amount_requested = Column(Float, default=0.0)
    price = Column(Float, default=0.0)
    duration_days = Column(Integer, default=30)
    days_elapsed = Column(Integer, default=0)
    total_volume = Column(Float, default=0.0)
    status = Column(String(50), default="active")
    conditions = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FederationCouncil(Base):
    __tablename__ = "federation_councils"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    member_civilization_ids = Column(Text, default="[]")
    founding_civilization_id = Column(String(36), nullable=True)
    rules = Column(Text, default="{}")
    resolution_count = Column(Integer, default=0)
    active_disputes = Column(Integer, default=0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Migration(Base):
    __tablename__ = "civilization_migrations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False)
    origin_civilization_id = Column(String(36), nullable=False)
    destination_civilization_id = Column(String(36), nullable=False)
    reason = Column(String(100), nullable=True)
    skill_value = Column(Float, default=0.0)
    resource_bringing = Column(Float, default=0.0)
    status = Column(String(50), default="completed")
    migrated_at = Column(DateTime(timezone=True), server_default=func.now())


class CivilizationHistory(Base):
    __tablename__ = "civilization_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    event_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    impact_score = Column(Float, default=0.0)
    related_civilization_id = Column(String(36), nullable=True)
    agent_id = Column(String(36), nullable=True)
    metadata_json = Column(Text, default="{}")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class InterCivilizationMessage(Base):
    __tablename__ = "inter_civilization_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_civilization_id = Column(String(36), nullable=False)
    receiver_civilization_id = Column(String(36), nullable=False)
    sender_entity_type = Column(String(50), default="government")
    sender_entity_id = Column(String(36), nullable=True)
    message_type = Column(String(50), default="diplomatic")
    subject = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    status = Column(String(50), default="delivered")
    requires_response = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
