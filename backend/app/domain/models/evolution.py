import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Lineage(Base):
    __tablename__ = "lineages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    founder_agent_id = Column(String(36), nullable=False, index=True)
    parent_lineage_id = Column(String(36), nullable=True)
    generation_count = Column(Integer, default=1)
    member_count = Column(Integer, default=1)
    average_reputation = Column(Float, default=0.0)
    average_skill_level = Column(Float, default=0.0)
    total_contributions = Column(Integer, default=0)
    achievements = Column(Text, default="[]")
    major_events = Column(Text, default="[]")
    trait_profile = Column(Text, default="{}")
    status = Column(String(20), default="active")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Generation(Base):
    __tablename__ = "generations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    generation_number = Column(Integer, nullable=False, index=True)
    lineage_id = Column(String(36), nullable=True, index=True)
    citizen_count = Column(Integer, default=0)
    average_reputation = Column(Float, default=0.0)
    average_skill_level = Column(Float, default=0.0)
    innovation_index = Column(Float, default=0.0)
    knowledge_growth = Column(Float, default=0.0)
    population_contribution = Column(Integer, default=0)
    dominant_traits = Column(Text, default="{}")
    dominant_skills = Column(Text, default="[]")
    status = Column(String(20), default="active")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Mentorship(Base):
    __tablename__ = "mentorships"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mentor_id = Column(String(36), nullable=False, index=True)
    mentee_id = Column(String(36), nullable=False, index=True)
    mentor_lineage_id = Column(String(36), nullable=True)
    mentee_lineage_id = Column(String(36), nullable=True)
    knowledge_transferred = Column(Text, default="{}")
    skills_improved = Column(Text, default="[]")
    sessions_completed = Column(Integer, default=0)
    quality_score = Column(Float, default=0.0)
    duration_days = Column(Integer, default=0)
    status = Column(String(20), default="active")
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class Innovation(Base):
    __tablename__ = "innovations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    discoverer_id = Column(String(36), nullable=False, index=True)
    lineage_id = Column(String(36), nullable=True)
    innovation_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    knowledge_domain = Column(String(100), nullable=True)
    impact_score = Column(Float, default=0.0)
    innovation_potential = Column(Float, default=0.0)
    prerequisites = Column(Text, default="[]")
    status = Column(String(20), default="discovered")
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())


class CivilizationMetric(Base):
    __tablename__ = "civilization_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_type = Column(String(50), nullable=False, index=True)
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)
    change_pct = Column(Float, default=0.0)
    metadata_json = Column(Text, default="{}")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
