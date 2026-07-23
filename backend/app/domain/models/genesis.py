import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class GenesisCivilization(Base):
    __tablename__ = "genesis_civilizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    population = Column(Integer, default=5)
    era = Column(String(50), default="primitive")
    creation_year = Column(Integer, default=0)
    current_year = Column(Integer, default=0)
    technology_level = Column(Float, default=0.0)
    culture_level = Column(Float, default=0.0)
    scientific_level = Column(Float, default=0.0)
    awareness_level = Column(Integer, default=0)
    has_discovered_simulation = Column(Integer, default=0)
    origin_story = Column(Text, nullable=True)
    status = Column(String(50), default="primitive")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class GenesisAgent(Base):
    __tablename__ = "genesis_agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(100), default="explorer")
    status = Column(String(50), default="alive")
    intelligence_level = Column(Float, default=0.3)
    survival_skill = Column(Float, default=0.3)
    learning_rate = Column(Float, default=0.1)
    social_influence = Column(Float, default=0.1)
    knowledge_areas = Column(Text, default="[]")
    energy = Column(Float, default=100.0)
    discovery_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BeliefSystem(Base):
    __tablename__ = "belief_systems"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)
    belief_type = Column(String(50), default="spiritual")
    origin_explanation = Column(Text, nullable=True)
    natural_event_explanations = Column(Text, default="{}")
    creator_concept = Column(Text, nullable=True)
    core_tenets = Column(Text, default="[]")
    rituals = Column(Text, default="[]")
    followers_count = Column(Integer, default=0)
    influence_level = Column(Float, default=0.0)
    status = Column(String(50), default="emerging")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Philosophy(Base):
    __tablename__ = "philosophies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    name = Column(String(255), nullable=False)
    philosopher_agent_id = Column(String(36), nullable=True)
    school_of_thought = Column(String(100), default="empiricism")
    core_ideas = Column(Text, default="[]")
    influence = Column(Float, default=0.0)
    followers = Column(Integer, default=0)
    status = Column(String(50), default="emerging")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CreatorInteraction(Base):
    __tablename__ = "creator_interactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    interaction_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    civilization_interpretation = Column(Text, nullable=True)
    impact_level = Column(Float, default=0.5)
    belief_impact = Column(Text, default="{}")
    triggered_by_creator = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HistoricalInterpretation(Base):
    __tablename__ = "historical_interpretations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    event_type = Column(String(100), nullable=False)
    actual_event = Column(Text, nullable=True)
    civilization_interpretation = Column(Text, nullable=True)
    impact_on_beliefs = Column(Text, default="{}")
    recorded_by_agent_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GenesisDiscovery(Base):
    __tablename__ = "genesis_discoveries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    discovery_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    discoverer_agent_id = Column(String(36), nullable=True)
    impact_level = Column(Float, default=0.3)
    era_recorded = Column(String(50), default="primitive")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EraRecord(Base):
    __tablename__ = "era_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    era_name = Column(String(100), nullable=False)
    start_year = Column(Integer, default=0)
    end_year = Column(Integer, nullable=True)
    key_events = Column(Text, default="[]")
    population_at_start = Column(Integer, default=0)
    technology_level = Column(Float, default=0.0)
    culture_level = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeDomain(Base):
    __tablename__ = "knowledge_domains"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    domain_name = Column(String(100), nullable=False)
    level = Column(Float, default=0.0)
    understanding = Column(Text, nullable=True)
    discoveries_made = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CreatorAwarenessRecord(Base):
    __tablename__ = "creator_awareness_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False)
    awareness_level = Column(Integer, default=0)
    understanding_description = Column(Text, nullable=True)
    evidence_collected = Column(Text, default="[]")
    philosopher_responsible = Column(String(255), nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
