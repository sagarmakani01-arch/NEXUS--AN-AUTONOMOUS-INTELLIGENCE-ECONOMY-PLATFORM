from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.domain.models.company import Company, CompanyFinance, CompanyMember, CompanyMemory, CompanyStrategy

logger = logging.getLogger("nexus.organization")


async def create_company(
    owner_id: str, name: str, description: str = "",
    industry: str = "", mission: str = "", vision: str = "",
    founder_agent_id: str | None = None, treasury_balance: float = 0,
) -> dict:
    async with async_session_factory() as session:
        company = Company(
            owner_id=owner_id, name=name, description=description,
            industry=industry, mission=mission, vision=vision,
            founder_agent_id=founder_agent_id, treasury_balance=treasury_balance,
            status="startup",
        )
        session.add(company)
        await session.commit()
        await session.refresh(company)
        return _company_to_dict(company)


async def get_company(company_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        return _company_to_dict(company) if company else None


async def list_companies(status: str = "", industry: str = "", skip: int = 0, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        q = select(Company)
        if status:
            q = q.where(Company.status == status)
        if industry:
            q = q.where(Company.industry == industry)
        q = q.order_by(Company.reputation.desc()).offset(skip).limit(limit)
        result = await session.execute(q)
        return [_company_to_dict(c) for c in result.scalars().all()]


async def update_company(company_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(company, k):
                setattr(company, k, v)
        await session.commit()
        await session.refresh(company)
        return _company_to_dict(company)


async def add_member(
    company_id: str, agent_id: str, role: str = "employee",
    department: str = "", title: str = "", salary: float = 0,
    reports_to: str | None = None,
) -> dict:
    async with async_session_factory() as session:
        existing = await session.execute(
            select(CompanyMember).where(
                CompanyMember.company_id == company_id,
                CompanyMember.agent_id == agent_id,
                CompanyMember.status == "active",
            )
        )
        if existing.scalar_one_or_none():
            return {"error": "Agent already a member"}

        member = CompanyMember(
            company_id=company_id, agent_id=agent_id, role=role,
            department=department, title=title, salary=salary,
            reports_to=reports_to,
        )
        session.add(member)
        company_result = await session.execute(select(Company).where(Company.id == company_id))
        company = company_result.scalar_one_or_none()
        if company:
            company.employee_count = (company.employee_count or 0) + 1
        await session.commit()
        await session.refresh(member)
        return _member_to_dict(member)


async def remove_member(company_id: str, agent_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(CompanyMember).where(
                CompanyMember.company_id == company_id,
                CompanyMember.agent_id == agent_id,
                CompanyMember.status == "active",
            )
        )
        member = result.scalar_one_or_none()
        if not member:
            return None
        member.status = "removed"
        company_result = await session.execute(select(Company).where(Company.id == company_id))
        company = company_result.scalar_one_or_none()
        if company and company.employee_count > 0:
            company.employee_count -= 1
        await session.commit()
        return _member_to_dict(member)


async def get_members(company_id: str, status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        q = select(CompanyMember).where(CompanyMember.company_id == company_id)
        if status:
            q = q.where(CompanyMember.status == status)
        q = q.order_by(CompanyMember.created_at)
        result = await session.execute(q)
        return [_member_to_dict(m) for m in result.scalars().all()]


async def get_member(company_id: str, agent_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(CompanyMember).where(
                CompanyMember.company_id == company_id,
                CompanyMember.agent_id == agent_id,
            )
        )
        member = result.scalar_one_or_none()
        return _member_to_dict(member) if member else None


async def update_member(member_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(CompanyMember).where(CompanyMember.id == member_id))
        member = result.scalar_one_or_none()
        if not member:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(member, k):
                setattr(member, k, v)
        await session.commit()
        await session.refresh(member)
        return _member_to_dict(member)


async def add_memory(company_id: str, event_type: str, title: str, description: str = "", importance: str = "medium") -> dict:
    async with async_session_factory() as session:
        memory = CompanyMemory(
            company_id=company_id, event_type=event_type,
            title=title, description=description, importance=importance,
        )
        session.add(memory)
        await session.commit()
        await session.refresh(memory)
        return _memory_to_dict(memory)


async def get_memories(company_id: str, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(CompanyMemory).where(CompanyMemory.company_id == company_id)
            .order_by(CompanyMemory.created_at.desc()).limit(limit)
        )
        return [_memory_to_dict(m) for m in result.scalars().all()]


async def create_strategy(
    company_id: str, title: str, description: str = "",
    strategy_type: str = "growth", goal: str = "",
    timeline_days: int = 30, expected_outcome: str = "",
) -> dict:
    async with async_session_factory() as session:
        strategy = CompanyStrategy(
            company_id=company_id, title=title, description=description,
            strategy_type=strategy_type, goal=goal,
            timeline_days=timeline_days, expected_outcome=expected_outcome,
        )
        session.add(strategy)
        await session.commit()
        await session.refresh(strategy)
        return _strategy_to_dict(strategy)


async def get_strategies(company_id: str, status: str = "") -> list[dict]:
    async with async_session_factory() as session:
        q = select(CompanyStrategy).where(CompanyStrategy.company_id == company_id)
        if status:
            q = q.where(CompanyStrategy.status == status)
        q = q.order_by(CompanyStrategy.created_at.desc())
        result = await session.execute(q)
        return [_strategy_to_dict(s) for s in result.scalars().all()]


async def update_strategy(strategy_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(CompanyStrategy).where(CompanyStrategy.id == strategy_id))
        strategy = result.scalar_one_or_none()
        if not strategy:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(strategy, k):
                setattr(strategy, k, v)
        await session.commit()
        await session.refresh(strategy)
        return _strategy_to_dict(strategy)


async def record_finance(
    company_id: str, transaction_type: str, amount: float,
    category: str = "", description: str = "",
    reference_id: str | None = None, reference_type: str | None = None,
    balance_after: float = 0,
) -> dict:
    async with async_session_factory() as session:
        finance = CompanyFinance(
            company_id=company_id, transaction_type=transaction_type,
            amount=amount, category=category, description=description,
            reference_id=reference_id, reference_type=reference_type,
            balance_after=balance_after,
        )
        session.add(finance)
        await session.commit()
        await session.refresh(finance)
        return _finance_to_dict(finance)


async def get_finances(company_id: str, limit: int = 100) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(CompanyFinance).where(CompanyFinance.company_id == company_id)
            .order_by(CompanyFinance.created_at.desc()).limit(limit)
        )
        return [_finance_to_dict(f) for f in result.scalars().all()]


async def get_company_stats() -> dict:
    async with async_session_factory() as session:
        status_counts = await session.execute(
            select(Company.status, func.count()).group_by(Company.status)
        )
        statuses = {row[0]: row[1] for row in status_counts.all()}

        industry_counts = await session.execute(
            select(Company.industry, func.count()).where(Company.industry.isnot(None)).group_by(Company.industry)
        )
        industries = {row[0]: row[1] for row in industry_counts.all()}

        avg_rep = await session.execute(select(func.avg(Company.reputation)))
        avg_reputation = avg_rep.scalar_one() or 0

        total_employees = await session.execute(select(func.sum(Company.employee_count)))
        total_emp = total_employees.scalar() or 0

        return {
            "statuses": statuses,
            "industries": industries,
            "total_companies": sum(statuses.values()),
            "avg_reputation": round(float(avg_reputation), 2),
            "total_employees": int(total_emp),
        }


def _company_to_dict(company: Company) -> dict:
    members = company.member_agent_ids
    if isinstance(members, str):
        try:
            members = json.loads(members)
        except (json.JSONDecodeError, TypeError):
            members = []
    depts = company.departments
    if isinstance(depts, str):
        try:
            depts = json.loads(depts)
        except (json.JSONDecodeError, TypeError):
            depts = []
    return {
        "id": company.id,
        "owner_id": company.owner_id,
        "founder_agent_id": company.founder_agent_id,
        "name": company.name,
        "description": company.description,
        "mission": company.mission,
        "vision": company.vision,
        "industry": company.industry,
        "status": company.status,
        "employee_count": company.employee_count,
        "treasury_balance": company.treasury_balance,
        "revenue": company.revenue,
        "expenses": company.expenses,
        "salary_budget": company.salary_budget,
        "reputation": company.reputation,
        "company_age": company.company_age,
        "total_projects": company.total_projects,
        "successful_projects": company.successful_projects,
        "failed_projects": company.failed_projects,
        "market_share": company.market_share,
        "growth_rate": company.growth_rate,
        "culture_score": company.culture_score,
        "member_agent_ids": members,
        "departments": depts,
        "metadata_": company.metadata_,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        "updated_at": company.updated_at.isoformat() if company.updated_at else None,
    }


def _member_to_dict(member: CompanyMember) -> dict:
    meta = member.metadata_
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except (json.JSONDecodeError, TypeError):
            meta = {}
    return {
        "id": member.id,
        "company_id": member.company_id,
        "agent_id": member.agent_id,
        "role": member.role,
        "department": member.department,
        "title": member.title,
        "salary": member.salary,
        "performance_score": member.performance_score,
        "hire_date": member.hire_date.isoformat() if member.hire_date else None,
        "status": member.status,
        "reports_to": member.reports_to,
        "metadata_": meta,
        "created_at": member.created_at.isoformat() if member.created_at else None,
        "updated_at": member.updated_at.isoformat() if member.updated_at else None,
    }


def _memory_to_dict(memory: CompanyMemory) -> dict:
    meta = memory.metadata_
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except (json.JSONDecodeError, TypeError):
            meta = {}
    return {
        "id": memory.id,
        "company_id": memory.company_id,
        "event_type": memory.event_type,
        "title": memory.title,
        "description": memory.description,
        "importance": memory.importance,
        "metadata_": meta,
        "created_at": memory.created_at.isoformat() if memory.created_at else None,
    }


def _strategy_to_dict(strategy: CompanyStrategy) -> dict:
    resources = strategy.resources_required
    if isinstance(resources, str):
        try:
            resources = json.loads(resources)
        except (json.JSONDecodeError, TypeError):
            resources = {}
    meta = strategy.metadata_
    if isinstance(meta, str):
        try:
            meta = json.loads(meta)
        except (json.JSONDecodeError, TypeError):
            meta = {}
    return {
        "id": strategy.id,
        "company_id": strategy.company_id,
        "title": strategy.title,
        "description": strategy.description,
        "strategy_type": strategy.strategy_type,
        "goal": strategy.goal,
        "resources_required": resources,
        "timeline_days": strategy.timeline_days,
        "progress": strategy.progress,
        "status": strategy.status,
        "expected_outcome": strategy.expected_outcome,
        "actual_outcome": strategy.actual_outcome,
        "metadata_": meta,
        "created_at": strategy.created_at.isoformat() if strategy.created_at else None,
        "updated_at": strategy.updated_at.isoformat() if strategy.updated_at else None,
        "completed_at": strategy.completed_at.isoformat() if strategy.completed_at else None,
    }


def _finance_to_dict(finance: CompanyFinance) -> dict:
    return {
        "id": finance.id,
        "company_id": finance.company_id,
        "transaction_type": finance.transaction_type,
        "amount": finance.amount,
        "category": finance.category,
        "description": finance.description,
        "reference_id": finance.reference_id,
        "reference_type": finance.reference_type,
        "balance_after": finance.balance_after,
        "created_at": finance.created_at.isoformat() if finance.created_at else None,
    }
