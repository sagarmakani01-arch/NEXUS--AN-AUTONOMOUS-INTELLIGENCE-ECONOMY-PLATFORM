import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class ResearchOrganization(Base):
    __tablename__ = "research_organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    org_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    founder_agent_id = Column(String(36), nullable=True)
    research_budget = Column(Float, default=0.0)
    reputation = Column(Float, default=50.0)
    research_areas = Column(Text, default="[]")
    scientist_agent_ids = Column(Text, default="[]")
    total_projects = Column(Integer, default=0)
    completed_projects = Column(Integer, default=0)
    published_papers = Column(Integer, default=0)
    citations_received = Column(Integer, default=0)
    technologies_developed = Column(Text, default="[]")
    knowledge_nodes_created = Column(Integer, default=0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ResearchProject(Base):
    __tablename__ = "research_projects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), nullable=True)
    lead_agent_id = Column(String(36), nullable=True)
    title = Column(String(500), nullable=False)
    research_question = Column(Text, nullable=False)
    hypothesis = Column(Text, nullable=True)
    objectives = Column(Text, default="[]")
    required_skills = Column(Text, default="[]")
    budget = Column(Float, default=0.0)
    budget_spent = Column(Float, default=0.0)
    timeline_days = Column(Integer, default=30)
    days_elapsed = Column(Integer, default=0)
    status = Column(String(50), default="proposed")
    priority = Column(String(20), default="medium")
    dependencies = Column(Text, default="[]")
    expected_impact = Column(Float, default=50.0)
    actual_impact = Column(Float, default=0.0)
    progress = Column(Float, default=0.0)
    team_agent_ids = Column(Text, default="[]")
    knowledge_domain = Column(String(100), nullable=True)
    funding_source = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    methodology = Column(Text, nullable=True)
    hypothesis = Column(Text, nullable=True)
    variables = Column(Text, default="{}")
    status = Column(String(50), default="planned")
    outcome = Column(String(50), nullable=True)
    outcome_details = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    time_spent = Column(Float, default=0.0)
    budget_consumed = Column(Float, default=0.0)
    compute_consumed = Column(Float, default=0.0)
    knowledge_produced = Column(Text, default="[]")
    unexpected_findings = Column(Text, default="[]")
    replicate_count = Column(Integer, default=0)
    replication_status = Column(String(50), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    node_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    maturity_level = Column(Float, default=0.1)
    confidence = Column(Float, default=0.5)
    novelty_score = Column(Float, default=1.0)
    utility_score = Column(Float, default=0.5)
    discovery_source = Column(String(36), nullable=True)
    discoverer_agent_id = Column(String(36), nullable=True)
    citations = Column(Integer, default=0)
    usage_count = Column(Integer, default=0)
    keywords = Column(Text, default="[]")
    data_payload = Column(Text, default="{}")
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id = Column(String(36), nullable=False)
    target_node_id = Column(String(36), nullable=False)
    edge_type = Column(String(50), nullable=False)
    weight = Column(Float, default=1.0)
    description = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5)
    created_by_agent_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Publication(Base):
    __tablename__ = "publications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    abstract = Column(Text, nullable=True)
    authors = Column(Text, default="[]")
    institution = Column(String(255), nullable=True)
    knowledge_domain = Column(String(100), nullable=True)
    keywords = Column(Text, default="[]")
    impact_score = Column(Float, default=0.0)
    citations = Column(Integer, default=0)
    quality_score = Column(Float, default=0.5)
    novelty_score = Column(Float, default=0.5)
    status = Column(String(50), default="draft")
    publication_date = Column(DateTime(timezone=True), nullable=True)
    project_id = Column(String(36), nullable=True)
    experiment_ids = Column(Text, default="[]")
    knowledge_node_ids = Column(Text, default="[]")
    references = Column(Text, default="[]")
    peer_review_status = Column(String(50), default="pending")
    open_access = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PeerReview(Base):
    __tablename__ = "peer_reviews"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    publication_id = Column(String(36), nullable=False)
    reviewer_agent_id = Column(String(36), nullable=False)
    institution = Column(String(255), nullable=True)
    decision = Column(String(50), nullable=False)
    confidence_rating = Column(Float, default=0.5)
    methodology_score = Column(Float, default=0.5)
    originality_score = Column(Float, default=0.5)
    significance_score = Column(Float, default=0.5)
    clarity_score = Column(Float, default=0.5)
    overall_score = Column(Float, default=0.5)
    comments = Column(Text, nullable=True)
    suggestions = Column(Text, default="[]")
    time_spent_hours = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Technology(Base):
    __tablename__ = "technologies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    tech_type = Column(String(50), nullable=False)
    domain = Column(String(100), nullable=True)
    difficulty_level = Column(Integer, default=1)
    prerequisites = Column(Text, default="[]")
    benefits = Column(Text, default="[]")
    unlock_conditions = Column(Text, default="{}")
    development_cost = Column(Float, default=0.0)
    research_points_needed = Column(Integer, default=100)
    research_points_earned = Column(Integer, default=0)
    adoption_count = Column(Integer, default=0)
    maturity = Column(Float, default=0.0)
    inventors = Column(Text, default="[]")
    organization_id = Column(String(36), nullable=True)
    status = Column(String(50), default="locked")
    unlocked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ResearchInnovation(Base):
    __tablename__ = "research_innovations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    innovation_type = Column(String(50), nullable=False)
    domain = Column(String(100), nullable=True)
    novelty_score = Column(Float, default=0.5)
    impact_score = Column(Float, default=0.5)
    feasibility_score = Column(Float, default=0.5)
    discoverer_agent_id = Column(String(36), nullable=True)
    organization_id = Column(String(36), nullable=True)
    project_id = Column(String(36), nullable=True)
    knowledge_node_ids = Column(Text, default="[]")
    status = Column(String(50), default="proposed")
    commercialization_potential = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Funding(Base):
    __tablename__ = "research_funding"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), nullable=False)
    funder_agent_id = Column(String(36), nullable=True)
    funder_organization = Column(String(255), nullable=True)
    funding_source_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    disbursed = Column(Float, default=0.0)
    conditions = Column(Text, default="[]")
    status = Column(String(50), default="pending")
    proposal_score = Column(Float, default=0.5)
    risk_assessment = Column(Float, default=0.5)
    expected_roi = Column(Float, default=1.0)
    granted_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Conference(Base):
    __tablename__ = "conferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=True)
    organizer_id = Column(String(36), nullable=True)
    location = Column(String(255), nullable=True)
    conference_type = Column(String(50), default="virtual")
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    attendee_count = Column(Integer, default=0)
    paper_count = Column(Integer, default=0)
    knowledge_shared = Column(Text, default="[]")
    status = Column(String(50), default="planned")
    reputation_impact = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ResearchMetrics(Base):
    __tablename__ = "research_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    organization_id = Column(String(36), nullable=True)
    metric_type = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)
    change_pct = Column(Float, default=0.0)
    period = Column(String(50), default="monthly")
    metadata_json = Column(Text, default="{}")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
