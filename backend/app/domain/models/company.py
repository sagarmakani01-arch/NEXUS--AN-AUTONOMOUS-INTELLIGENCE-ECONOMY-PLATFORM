import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    founder_agent_id = Column(String(36), nullable=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    mission = Column(Text, nullable=True)
    vision = Column(Text, nullable=True)
    industry = Column(String(100), nullable=True)
    status = Column(String(50), default="startup")
    employee_count = Column(Integer, default=0)
    treasury_balance = Column(Float, default=0.0)
    revenue = Column(Float, default=0.0)
    expenses = Column(Float, default=0.0)
    salary_budget = Column(Float, default=0.0)
    reputation = Column(Float, default=50.0)
    company_age = Column(Integer, default=0)
    total_projects = Column(Integer, default=0)
    successful_projects = Column(Integer, default=0)
    failed_projects = Column(Integer, default=0)
    market_share = Column(Float, default=0.0)
    growth_rate = Column(Float, default=0.0)
    culture_score = Column(Float, default=50.0)
    member_agent_ids = Column(Text, default="[]")
    departments = Column(Text, default="[]")
    metadata_ = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", backref="companies")


class CompanyMember(Base):
    __tablename__ = "company_members"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    role = Column(String(50), default="employee")
    department = Column(String(100), nullable=True)
    title = Column(String(255), nullable=True)
    salary = Column(Float, default=0.0)
    performance_score = Column(Float, default=50.0)
    hire_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(50), default="active")
    reports_to = Column(String(36), nullable=True)
    metadata_ = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CompanyMemory(Base):
    __tablename__ = "company_memories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    event_type = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    importance = Column(String(20), default="medium")
    metadata_ = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CompanyStrategy(Base):
    __tablename__ = "company_strategies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    strategy_type = Column(String(50), default="growth")
    goal = Column(Text, nullable=True)
    resources_required = Column(Text, default="{}")
    timeline_days = Column(Integer, default=30)
    progress = Column(Float, default=0.0)
    status = Column(String(50), default="active")
    expected_outcome = Column(Text, nullable=True)
    actual_outcome = Column(Text, nullable=True)
    metadata_ = Column("metadata", Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class CompanyFinance(Base):
    __tablename__ = "company_finances"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    transaction_type = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    reference_id = Column(String(36), nullable=True)
    reference_type = Column(String(50), nullable=True)
    balance_after = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
