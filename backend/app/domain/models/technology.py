import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Technology(Base):
    __tablename__ = "tech_evolutions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    domain = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tech_type = Column(String(50), nullable=False)
    origin_civilization_id = Column(String(36), nullable=True)
    discovery_date = Column(DateTime(timezone=True), nullable=True)
    required_knowledge = Column(Text, default="[]")
    required_resources = Column(Text, default="{}")
    difficulty_level = Column(Float, default=50.0)
    impact_score = Column(Float, default=0.0)
    current_level = Column(Float, default=0.0)
    applications = Column(Text, default="[]")
    prerequisites = Column(Text, default="[]")
    maturity = Column(Float, default=0.0)
    adoption_count = Column(Integer, default=0)
    status = Column(String(50), default="concept")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TechnologyEdge(Base):
    __tablename__ = "technology_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_technology_id = Column(String(36), nullable=False, index=True)
    target_technology_id = Column(String(36), nullable=False, index=True)
    edge_type = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TechnologyDiscovery(Base):
    __tablename__ = "technology_discoveries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    technology_id = Column(String(36), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(50), default="medium")
    impact_score = Column(Float, default=0.0)
    discoverer_agent_id = Column(String(36), nullable=True)
    method = Column(String(100), default="research")
    confidence = Column(Float, default=50.0)
    status = Column(String(50), default="discovered")
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())


class TechnologyDevelopment(Base):
    __tablename__ = "technology_developments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    technology_id = Column(String(36), nullable=False, index=True)
    civilization_id = Column(String(36), nullable=False, index=True)
    stage = Column(String(50), nullable=False)
    progress = Column(Float, default=0.0)
    resource_cost = Column(Float, default=0.0)
    time_spent = Column(Float, default=0.0)
    lead_agent_id = Column(String(36), nullable=True)
    team_agent_ids = Column(Text, default="[]")
    notes = Column(Text, nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TechnologyAdoption(Base):
    __tablename__ = "technology_adoptions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    technology_id = Column(String(36), nullable=False, index=True)
    decision = Column(String(50), nullable=False)
    economic_benefit = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    risk = Column(Float, default=0.0)
    cultural_compatibility = Column(Float, default=50.0)
    strategic_importance = Column(Float, default=50.0)
    decided_at = Column(DateTime(timezone=True), server_default=func.now())


class ScientificOrganization(Base):
    __tablename__ = "scientific_organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    org_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    research_output = Column(Float, default=0.0)
    discoveries_count = Column(Integer, default=0)
    scientist_count = Column(Integer, default=0)
    funding_level = Column(Float, default=50.0)
    reputation = Column(Float, default=50.0)
    specialization = Column(Text, default="[]")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Scientist(Base):
    __tablename__ = "scientists"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    agent_id = Column(String(36), nullable=True)
    name = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False)
    organization_id = Column(String(36), nullable=True)
    research_output = Column(Float, default=0.0)
    discoveries_count = Column(Integer, default=0)
    publications_count = Column(Integer, default=0)
    influence_score = Column(Float, default=0.0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CivilizationTechLevel(Base):
    __tablename__ = "civilization_tech_levels"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, unique=True, index=True)
    computational_capability = Column(Float, default=10.0)
    energy_capability = Column(Float, default=10.0)
    manufacturing_capability = Column(Float, default=10.0)
    scientific_knowledge = Column(Float, default=10.0)
    automation_level = Column(Float, default=5.0)
    infrastructure_level = Column(Float, default=10.0)
    current_era = Column(String(100), default="pre_industrial")
    last_calculated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TechnologyTimeline(Base):
    __tablename__ = "technology_timelines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    civilization_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    technology_id = Column(String(36), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    impact_score = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
