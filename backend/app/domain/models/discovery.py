import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class ScientificExperiment(Base):
    __tablename__ = "scientific_experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    research_question = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)
    variables = Column(Text, default="{}")
    constraints = Column(Text, default="{}")
    simulation_params = Column(Text, default="{}")
    duration_ticks = Column(Integer, default=100)
    status = Column(String(50), default="draft")
    result_summary = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    created_by = Column(String(255), nullable=True)
    laboratory_type = Column(String(100), default="general")
    tags = Column(Text, default="[]")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AutomatedExperiment(Base):
    __tablename__ = "automated_experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    trigger_observation = Column(Text, nullable=True)
    experiment_type = Column(String(100), default="correlation")
    variable_name = Column(String(255), nullable=True)
    variable_change = Column(String(255), nullable=True)
    duration_ticks = Column(Integer, default=50)
    status = Column(String(50), default="pending")
    result_summary = Column(Text, nullable=True)
    significance = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiscoveredPattern(Base):
    __tablename__ = "discovery_patterns"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pattern_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    antecedent = Column(Text, nullable=True)
    consequent = Column(Text, nullable=True)
    confidence = Column(Float, default=0.0)
    support = Column(Float, default=0.0)
    lift = Column(Float, default=0.0)
    sample_size = Column(Integer, default=0)
    method = Column(String(100), default="statistical")
    tags = Column(Text, default="[]")
    status = Column(String(50), default="discovered")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Hypothesis(Base):
    __tablename__ = "scientific_hypotheses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    phenomenon = Column(Text, nullable=True)
    proposed_explanation = Column(Text, nullable=True)
    supporting_evidence = Column(Text, default="[]")
    counterexamples = Column(Text, default="[]")
    confidence_level = Column(Float, default=0.0)
    status = Column(String(50), default="proposed")
    domain = Column(String(100), default="general")
    created_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HypothesisValidation(Base):
    __tablename__ = "hypothesis_validations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hypothesis_id = Column(String(36), nullable=False)
    experiment_id = Column(String(36), nullable=True)
    validation_type = Column(String(100), default="experiment")
    outcome = Column(String(50), default="inconclusive")
    confidence_delta = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScienceKnowledgeNode(Base):
    __tablename__ = "science_knowledge_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_type = Column(String(100), nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    data = Column(Text, default="{}")
    importance = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScienceKnowledgeEdge(Base):
    __tablename__ = "science_knowledge_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id = Column(String(36), nullable=False)
    target_node_id = Column(String(36), nullable=False)
    edge_type = Column(String(100), nullable=False)
    weight = Column(Float, default=0.5)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResearchLaboratory(Base):
    __tablename__ = "research_laboratories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    lab_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    specialization = Column(Text, default="[]")
    experiment_count = Column(Integer, default=0)
    active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResearchAgent(Base):
    __tablename__ = "research_agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    specialization = Column(String(100), nullable=False)
    laboratory_id = Column(String(36), nullable=True)
    experiments_conducted = Column(Integer, default=0)
    patterns_discovered = Column(Integer, default=0)
    reports_written = Column(Integer, default=0)
    accuracy_score = Column(Float, default=0.5)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResearchReport(Base):
    __tablename__ = "research_reports"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    research_question = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    simulation_setup = Column(Text, nullable=True)
    results = Column(Text, nullable=True)
    limitations = Column(Text, nullable=True)
    future_experiments = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    status = Column(String(50), default="draft")
    created_by_agent_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DiscoveryArchive(Base):
    __tablename__ = "discovery_archives"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    archive_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=True)
    reference_id = Column(String(36), nullable=True)
    success = Column(Integer, default=1)
    tags = Column(Text, default="[]")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SimulationSnapshot(Base):
    __tablename__ = "science_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    snapshot_type = Column(String(100), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, default=0.0)
    tick = Column(Integer, default=0)
    civilization_id = Column(String(36), nullable=True)
    metadata_json = Column(Text, default="{}")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
