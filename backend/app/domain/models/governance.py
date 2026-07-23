import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class GovernanceEntity(Base):
    __tablename__ = "governance_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    entity_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    authority_level = Column(String(30), nullable=False, default="individual")
    founder_id = Column(String(36), nullable=True)
    member_ids = Column(Text, default="[]")
    policy_ids = Column(Text, default="[]")
    law_ids = Column(Text, default="[]")
    resources = Column(Text, default="{}")
    reputation = Column(Float, default=50.0)
    status = Column(String(20), default="active")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())


class Law(Base):
    __tablename__ = "laws"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String(36), nullable=False)
    creator_type = Column(String(20), default="government")
    scope = Column(String(50), nullable=False, default="global")
    affected_entities = Column(Text, default="[]")
    category = Column(String(50), default="general")
    severity = Column(String(20), default="medium")
    penalty = Column(Text, default="{}")
    status = Column(String(20), default="active")
    effective_date = Column(DateTime(timezone=True), server_default=func.now())
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    policy_type = Column(String(50), nullable=False)
    creator_id = Column(String(36), nullable=False)
    target = Column(String(255), nullable=True)
    rules = Column(Text, default="{}")
    expected_outcome = Column(Text, nullable=True)
    duration_days = Column(Integer, default=30)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="active")
    compliance_rate = Column(Float, default=100.0)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class Tax(Base):
    __tablename__ = "taxes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    tax_type = Column(String(50), nullable=False)
    rate = Column(Float, nullable=False)
    target = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    creator_id = Column(String(36), nullable=False)
    revenue_total = Column(Float, default=0.0)
    revenue_use = Column(Text, default="infrastructure")
    status = Column(String(20), default="active")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Regulation(Base):
    __tablename__ = "regulations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    regulation_type = Column(String(50), nullable=False)
    authority_id = Column(String(36), nullable=False)
    target_sector = Column(String(100), nullable=True)
    requirements = Column(Text, default="{}")
    max_violations = Column(Integer, default=3)
    penalty_description = Column(Text, nullable=True)
    status = Column(String(20), default="active")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plaintiff_id = Column(String(36), nullable=False, index=True)
    plaintiff_type = Column(String(20), default="agent")
    defendant_id = Column(String(36), nullable=False, index=True)
    defendant_type = Column(String(20), default="agent")
    conflict_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    evidence = Column(Text, default="[]")
    resolution_method = Column(String(30), default="arbitration")
    resolution = Column(Text, nullable=True)
    ruling = Column(Text, nullable=True)
    penalty_amount = Column(Float, default=0.0)
    arbitrator_id = Column(String(36), nullable=True)
    status = Column(String(20), default="open")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class Vote(Base):
    __tablename__ = "votes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    proposal_title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    proposer_id = Column(String(36), nullable=False)
    proposal_type = Column(String(50), default="law")
    target_id = Column(String(36), nullable=True)
    options = Column(Text, default='["yes","no"]')
    voters = Column(Text, default="{}")
    tally = Column(Text, default="{}")
    total_eligible = Column(Integer, default=0)
    quorum_pct = Column(Float, default=30.0)
    status = Column(String(20), default="open")
    result = Column(Text, nullable=True)
    weight_factor = Column(String(30), default="equal")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closes_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class GovernanceRecord(Base):
    __tablename__ = "governance_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    record_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    entity_id = Column(String(36), nullable=True)
    actor_id = Column(String(36), nullable=False)
    actor_type = Column(String(20), default="government")
    related_ids = Column(Text, default="[]")
    impact = Column(Text, default="{}")
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
