from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.domain.models.contract import Contract
from app.domain.models.proposal import Proposal
from app.domain.models.task import Task

logger = logging.getLogger("nexus.marketplace")


async def create_task(
    posted_by: str, title: str, description: str = "",
    required_skills: list[str] | None = None, reward: float = 0,
    priority: str = "medium", deadline: datetime | None = None,
) -> dict:
    async with async_session_factory() as session:
        task = Task(
            posted_by=posted_by, title=title, description=description,
            required_skills=json.dumps(required_skills or []),
            reward=reward, priority=priority, deadline=deadline, status="open",
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return _task_to_dict(task)


async def get_task(task_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        return _task_to_dict(task) if task else None


async def list_tasks(status: str = "", priority: str = "", skip: int = 0, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        q = select(Task)
        if status:
            q = q.where(Task.status == status)
        if priority:
            q = q.where(Task.priority == priority)
        q = q.order_by(Task.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(q)
        return [_task_to_dict(t) for t in result.scalars().all()]


async def update_task(task_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(task, k):
                setattr(task, k, v)
        await session.commit()
        await session.refresh(task)
        return _task_to_dict(task)


async def search_tasks(query: str = "", skills: list[str] | None = None, min_reward: float = 0) -> list[dict]:
    async with async_session_factory() as session:
        q = select(Task).where(Task.status == "open")
        if query:
            q = q.where(Task.title.contains(query) | Task.description.contains(query))
        if min_reward > 0:
            q = q.where(Task.reward >= min_reward)
        q = q.order_by(Task.reward.desc()).limit(100)
        result = await session.execute(q)
        tasks = [_task_to_dict(t) for t in result.scalars().all()]
        if skills:
            tasks = [t for t in tasks if any(s in t.get("required_skills", []) for s in skills)]
        return tasks


async def count_tasks_by_status() -> dict:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Task.status, func.count()).group_by(Task.status)
        )
        return {row[0]: row[1] for row in result.all()}


async def create_proposal(
    task_id: str, agent_id: str, proposed_reward: float,
    cover_letter: str = "", estimated_duration: str = "",
) -> dict:
    async with async_session_factory() as session:
        proposal = Proposal(
            task_id=task_id, agent_id=agent_id, proposed_reward=proposed_reward,
            cover_letter=cover_letter, estimated_duration=estimated_duration,
            status="pending",
        )
        session.add(proposal)
        await session.commit()
        await session.refresh(proposal)
        return _proposal_to_dict(proposal)


async def get_proposal(proposal_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        return _proposal_to_dict(proposal) if proposal else None


async def list_proposals_for_task(task_id: str) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Proposal).where(Proposal.task_id == task_id).order_by(Proposal.created_at.desc())
        )
        return [_proposal_to_dict(p) for p in result.scalars().all()]


async def list_proposals_by_agent(agent_id: str, status: str = "") -> list[dict]:
    async with async_session_factory() as session:
        q = select(Proposal).where(Proposal.agent_id == agent_id)
        if status:
            q = q.where(Proposal.status == status)
        q = q.order_by(Proposal.created_at.desc()).limit(50)
        result = await session.execute(q)
        return [_proposal_to_dict(p) for p in result.scalars().all()]


async def update_proposal(proposal_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        if not proposal:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(proposal, k):
                setattr(proposal, k, v)
        await session.commit()
        await session.refresh(proposal)
        return _proposal_to_dict(proposal)


async def create_contract(
    task_id: str, proposal_id: str, poster_id: str, agent_id: str,
    agreed_reward: float, terms: str = "",
) -> dict:
    async with async_session_factory() as session:
        contract = Contract(
            task_id=task_id, proposal_id=proposal_id, poster_id=poster_id,
            agent_id=agent_id, agreed_reward=agreed_reward, terms=terms,
            status="created",
        )
        session.add(contract)
        await session.commit()
        await session.refresh(contract)
        return _contract_to_dict(contract)


async def get_contract(contract_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()
        return _contract_to_dict(contract) if contract else None


async def list_contracts_for_task(task_id: str) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Contract).where(Contract.task_id == task_id).order_by(Contract.created_at.desc())
        )
        return [_contract_to_dict(c) for c in result.scalars().all()]


async def list_contracts_by_agent(agent_id: str, status: str = "") -> list[dict]:
    async with async_session_factory() as session:
        q = select(Contract).where(Contract.agent_id == agent_id)
        if status:
            q = q.where(Contract.status == status)
        q = q.order_by(Contract.created_at.desc()).limit(50)
        result = await session.execute(q)
        return [_contract_to_dict(c) for c in result.scalars().all()]


async def list_contracts_by_poster(poster_id: str, status: str = "") -> list[dict]:
    async with async_session_factory() as session:
        q = select(Contract).where(Contract.poster_id == poster_id)
        if status:
            q = q.where(Contract.status == status)
        q = q.order_by(Contract.created_at.desc()).limit(50)
        result = await session.execute(q)
        return [_contract_to_dict(c) for c in result.scalars().all()]


async def update_contract(contract_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Contract).where(Contract.id == contract_id))
        contract = result.scalar_one_or_none()
        if not contract:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(contract, k):
                setattr(contract, k, v)
        await session.commit()
        await session.refresh(contract)
        return _contract_to_dict(contract)


async def get_marketplace_stats() -> dict:
    async with async_session_factory() as session:
        task_counts = await session.execute(
            select(Task.status, func.count()).group_by(Task.status)
        )
        tasks = {row[0]: row[1] for row in task_counts.all()}

        proposal_counts = await session.execute(
            select(Proposal.status, func.count()).group_by(Proposal.status)
        )
        proposals = {row[0]: row[1] for row in proposal_counts.all()}

        contract_counts = await session.execute(
            select(Contract.status, func.count()).group_by(Contract.status)
        )
        contracts = {row[0]: row[1] for row in contract_counts.all()}

        total_reward = await session.execute(select(func.sum(Task.reward)).where(Task.status == "completed"))
        total_volume = total_reward.scalar_one() or 0

        avg_reward = await session.execute(select(func.avg(Task.reward)).where(Task.status == "open"))
        avg = avg_reward.scalar_one() or 0

        return {
            "tasks": tasks,
            "proposals": proposals,
            "contracts": contracts,
            "total_tasks": sum(tasks.values()),
            "total_proposals": sum(proposals.values()),
            "total_contracts": sum(contracts.values()),
            "total_volume": round(float(total_volume), 2),
            "avg_task_reward": round(float(avg), 2),
        }


def _task_to_dict(task: Task) -> dict:
    skills = task.required_skills
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except (json.JSONDecodeError, TypeError):
            skills = []
    return {
        "id": task.id,
        "posted_by": task.posted_by,
        "title": task.title,
        "description": task.description,
        "required_skills": skills or [],
        "reward": task.reward,
        "status": task.status,
        "priority": task.priority,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "result": task.result,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def _proposal_to_dict(proposal: Proposal) -> dict:
    return {
        "id": proposal.id,
        "task_id": proposal.task_id,
        "agent_id": proposal.agent_id,
        "proposed_reward": proposal.proposed_reward,
        "cover_letter": proposal.cover_letter,
        "estimated_duration": proposal.estimated_duration,
        "status": proposal.status,
        "counter_reward": proposal.counter_reward,
        "counter_message": proposal.counter_message,
        "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
        "updated_at": proposal.updated_at.isoformat() if proposal.updated_at else None,
    }


def _contract_to_dict(contract: Contract) -> dict:
    return {
        "id": contract.id,
        "task_id": contract.task_id,
        "proposal_id": contract.proposal_id,
        "poster_id": contract.poster_id,
        "agent_id": contract.agent_id,
        "agreed_reward": contract.agreed_reward,
        "status": contract.status,
        "terms": contract.terms,
        "result": contract.result,
        "rating": contract.rating,
        "feedback": contract.feedback,
        "created_at": contract.created_at.isoformat() if contract.created_at else None,
        "accepted_at": contract.accepted_at.isoformat() if contract.accepted_at else None,
        "started_at": contract.started_at.isoformat() if contract.started_at else None,
        "completed_at": contract.completed_at.isoformat() if contract.completed_at else None,
        "failed_at": contract.failed_at.isoformat() if contract.failed_at else None,
    }
