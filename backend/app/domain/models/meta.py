import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class UniverseObservation(Base):
    __tablename__ = "universe_observations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_id = Column(String(36), nullable=True, index=True)
    tick = Column(Integer, nullable=False)
    year = Column(Integer, nullable=True)
    population = Column(Integer, default=0)
    economy_gdp = Column(Float, default=0.0)
    research_level = Column(Float, default=0.0)
    technology_level = Column(Float, default=0.0)
    education_index = Column(Float, default=0.0)
    governance_stability = Column(Float, default=0.0)
    environment_health = Column(Float, default=0.0)
    innovation_rate = Column(Float, default=0.0)
    social_stability = Column(Float, default=0.0)
    resource_scarcity = Column(Float, default=0.0)
    event_count = Column(Integer, default=0)
    civilization_id = Column(String(36), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CrossSimulationResult(Base):
    __tablename__ = "cross_simulation_results"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    simulation_a_id = Column(String(36), nullable=False)
    simulation_b_id = Column(String(36), nullable=False)
    comparison_type = Column(String(100), nullable=False)
    metric = Column(String(100), nullable=False)
    value_a = Column(Float, default=0.0)
    value_b = Column(Float, default=0.0)
    difference = Column(Float, default=0.0)
    percent_change = Column(Float, default=0.0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiscoveredPattern(Base):
    __tablename__ = "discovered_patterns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    antecedent = Column(String(500), nullable=True)
    consequent = Column(String(500), nullable=True)
    confidence = Column(Float, default=0.0)
    support = Column(Float, default=0.0)
    lift = Column(Float, default=0.0)
    sample_size = Column(Integer, default=0)
    evidence = Column(Text, default="[]")
    tags = Column(Text, default="[]")
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RuleEvaluation(Base):
    __tablename__ = "rule_evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_name = Column(String(255), nullable=False)
    rule_domain = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    effectiveness = Column(Float, default=0.0)
    stability = Column(Float, default=0.0)
    side_effects = Column(Text, nullable=True)
    evidence = Column(Text, default="[]")
    report = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Experiment(Base):
    __tablename__ = "meta_experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    experiment_type = Column(String(100), nullable=False)
    control_id = Column(String(36), nullable=True)
    variable_name = Column(String(255), nullable=True)
    variable_change = Column(Text, nullable=True)
    duration_ticks = Column(Integer, default=100)
    status = Column(String(50), default="pending")
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class Recommendation(Base):
    __tablename__ = "meta_recommendations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    recommendation_type = Column(String(100), nullable=False)
    target_domain = Column(String(100), nullable=True)
    suggested_change = Column(Text, nullable=True)
    expected_impact = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    evidence = Column(Text, default="[]")
    supporting_simulations = Column(Text, default="[]")
    limitations = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeEntry(Base):
    __tablename__ = "knowledge_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    entry_type = Column(String(100), nullable=False)
    source = Column(String(255), nullable=True)
    tags = Column(Text, default="[]")
    confidence = Column(Float, default=0.0)
    related_entries = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SimulationReport(Base):
    __tablename__ = "simulation_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    report_type = Column(String(100), nullable=False)
    content = Column(Text, nullable=True)
    data = Column(Text, default="{}")
    simulation_ids = Column(Text, default="[]")
    tags = Column(Text, default="[]")
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
