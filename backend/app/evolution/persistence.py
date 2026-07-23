import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.evolution import (
    Lineage, Generation, Mentorship, Innovation, CivilizationMetric,
)

logger = logging.getLogger("nexus.evolution")


async def create_lineage(name: str, founder_agent_id: str,
                         parent_lineage_id: str | None = None,
                         trait_profile: dict | None = None) -> str:
    async with async_session_factory() as session:
        lineage = Lineage(
            name=name, founder_agent_id=founder_agent_id,
            parent_lineage_id=parent_lineage_id,
            trait_profile=json.dumps(trait_profile or {}),
        )
        session.add(lineage)
        await session.commit()
        return lineage.id


async def get_lineage(lineage_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Lineage).where(Lineage.id == lineage_id))
        l = result.scalar_one_or_none()
        if not l:
            return None
        return _lineage_to_dict(l)


async def list_lineages(status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Lineage).where(Lineage.status == status)
            .order_by(Lineage.member_count.desc())
        )
        return [_lineage_to_dict(l) for l in result.scalars().all()]


async def update_lineage(lineage_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Lineage).where(Lineage.id == lineage_id))
        l = result.scalar_one_or_none()
        if l:
            for k, v in kwargs.items():
                if hasattr(l, k):
                    setattr(l, k, v)
            l.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_generation(generation_number: int, lineage_id: str | None = None,
                            citizen_count: int = 0) -> str:
    async with async_session_factory() as session:
        gen = Generation(
            generation_number=generation_number, lineage_id=lineage_id,
            citizen_count=citizen_count,
        )
        session.add(gen)
        await session.commit()
        return gen.id


async def get_generation(generation_number: int, lineage_id: str | None = None) -> dict | None:
    async with async_session_factory() as session:
        stmt = select(Generation).where(Generation.generation_number == generation_number)
        if lineage_id:
            stmt = stmt.where(Generation.lineage_id == lineage_id)
        result = await session.execute(stmt)
        g = result.scalar_one_or_none()
        if not g:
            return None
        return _generation_to_dict(g)


async def list_generations(lineage_id: str | None = None, limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Generation)
        if lineage_id:
            stmt = stmt.where(Generation.lineage_id == lineage_id)
        stmt = stmt.order_by(Generation.generation_number.desc()).limit(limit)
        result = await session.execute(stmt)
        return [_generation_to_dict(g) for g in result.scalars().all()]


async def update_generation(generation_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Generation).where(Generation.id == generation_id))
        g = result.scalar_one_or_none()
        if g:
            for k, v in kwargs.items():
                if hasattr(g, k):
                    setattr(g, k, v)
            await session.commit()


async def create_mentorship(mentor_id: str, mentee_id: str,
                            mentor_lineage_id: str | None = None,
                            mentee_lineage_id: str | None = None) -> str:
    async with async_session_factory() as session:
        m = Mentorship(
            mentor_id=mentor_id, mentee_id=mentee_id,
            mentor_lineage_id=mentor_lineage_id,
            mentee_lineage_id=mentee_lineage_id,
        )
        session.add(m)
        await session.commit()
        return m.id


async def get_mentorships(mentor_id: str | None = None, mentee_id: str | None = None,
                          status: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Mentorship)
        conditions = []
        if mentor_id:
            conditions.append(Mentorship.mentor_id == mentor_id)
        if mentee_id:
            conditions.append(Mentorship.mentee_id == mentee_id)
        if status:
            conditions.append(Mentorship.status == status)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Mentorship.started_at.desc())
        result = await session.execute(stmt)
        return [_mentorship_to_dict(m) for m in result.scalars().all()]


async def update_mentorship(mentorship_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Mentorship).where(Mentorship.id == mentorship_id))
        m = result.scalar_one_or_none()
        if m:
            for k, v in kwargs.items():
                if hasattr(m, k):
                    setattr(m, k, v)
            await session.commit()


async def create_innovation(discoverer_id: str, innovation_type: str, title: str,
                            description: str | None = None,
                            knowledge_domain: str | None = None,
                            impact_score: float = 0.0,
                            innovation_potential: float = 0.0,
                            lineage_id: str | None = None) -> str:
    async with async_session_factory() as session:
        inn = Innovation(
            discoverer_id=discoverer_id, lineage_id=lineage_id,
            innovation_type=innovation_type, title=title,
            description=description, knowledge_domain=knowledge_domain,
            impact_score=impact_score, innovation_potential=innovation_potential,
        )
        session.add(inn)
        await session.commit()
        return inn.id


async def list_innovations(discoverer_id: str | None = None,
                           innovation_type: str | None = None,
                           limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Innovation)
        conditions = []
        if discoverer_id:
            conditions.append(Innovation.discoverer_id == discoverer_id)
        if innovation_type:
            conditions.append(Innovation.innovation_type == innovation_type)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Innovation.discovered_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return [
            {
                "id": i.id, "discoverer_id": i.discoverer_id,
                "lineage_id": i.lineage_id,
                "innovation_type": i.innovation_type,
                "title": i.title, "description": i.description,
                "knowledge_domain": i.knowledge_domain,
                "impact_score": i.impact_score,
                "innovation_potential": i.innovation_potential,
                "status": i.status,
                "discovered_at": i.discovered_at.isoformat() if i.discovered_at else None,
            }
            for i in result.scalars().all()
        ]


async def record_metric(metric_type: str, value: float,
                         previous_value: float | None = None,
                         metadata: dict | None = None) -> str:
    async with async_session_factory() as session:
        change_pct = 0.0
        if previous_value and previous_value != 0:
            change_pct = round((value - previous_value) / previous_value * 100, 2)
        metric = CivilizationMetric(
            metric_type=metric_type, value=value,
            previous_value=previous_value, change_pct=change_pct,
            metadata_json=json.dumps(metadata or {}),
        )
        session.add(metric)
        await session.commit()
        return metric.id


async def get_metrics(metric_type: str | None = None, limit: int = 30) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(CivilizationMetric)
        if metric_type:
            stmt = stmt.where(CivilizationMetric.metric_type == metric_type)
        stmt = stmt.order_by(CivilizationMetric.recorded_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return [
            {
                "id": m.id, "metric_type": m.metric_type,
                "value": m.value, "previous_value": m.previous_value,
                "change_pct": m.change_pct,
                "recorded_at": m.recorded_at.isoformat() if m.recorded_at else None,
            }
            for m in result.scalars().all()
        ]


async def get_latest_metric(metric_type: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(CivilizationMetric)
            .where(CivilizationMetric.metric_type == metric_type)
            .order_by(CivilizationMetric.recorded_at.desc())
            .limit(1)
        )
        m = result.scalar_one_or_none()
        if not m:
            return None
        return {
            "id": m.id, "metric_type": m.metric_type,
            "value": m.value, "previous_value": m.previous_value,
            "change_pct": m.change_pct,
        }


async def get_evolution_stats() -> dict:
    async with async_session_factory() as session:
        lineages = await session.execute(select(func.count(Lineage.id)))
        generations = await session.execute(select(func.count(Generation.id)))
        mentorships = await session.execute(select(func.count(Mentorship.id)))
        innovations = await session.execute(select(func.count(Innovation.id)))
        active_mentorships = await session.execute(
            select(func.count(Mentorship.id)).where(Mentorship.status == "active")
        )
        return {
            "total_lineages": lineages.scalar() or 0,
            "total_generations": generations.scalar() or 0,
            "total_mentorships": mentorships.scalar() or 0,
            "total_innovations": innovations.scalar() or 0,
            "active_mentorships": active_mentorships.scalar() or 0,
        }


def _lineage_to_dict(l: Lineage) -> dict:
    return {
        "id": l.id, "name": l.name,
        "founder_agent_id": l.founder_agent_id,
        "parent_lineage_id": l.parent_lineage_id,
        "generation_count": l.generation_count,
        "member_count": l.member_count,
        "average_reputation": l.average_reputation,
        "average_skill_level": l.average_skill_level,
        "total_contributions": l.total_contributions,
        "achievements": json.loads(l.achievements) if l.achievements else [],
        "major_events": json.loads(l.major_events) if l.major_events else [],
        "trait_profile": json.loads(l.trait_profile) if l.trait_profile else {},
        "status": l.status,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }


def _generation_to_dict(g: Generation) -> dict:
    return {
        "id": g.id, "generation_number": g.generation_number,
        "lineage_id": g.lineage_id,
        "citizen_count": g.citizen_count,
        "average_reputation": g.average_reputation,
        "average_skill_level": g.average_skill_level,
        "innovation_index": g.innovation_index,
        "knowledge_growth": g.knowledge_growth,
        "dominant_traits": json.loads(g.dominant_traits) if g.dominant_traits else {},
        "dominant_skills": json.loads(g.dominant_skills) if g.dominant_skills else [],
        "status": g.status,
        "created_at": g.created_at.isoformat() if g.created_at else None,
    }


def _mentorship_to_dict(m: Mentorship) -> dict:
    return {
        "id": m.id, "mentor_id": m.mentor_id,
        "mentee_id": m.mentee_id,
        "mentor_lineage_id": m.mentor_lineage_id,
        "mentee_lineage_id": m.mentee_lineage_id,
        "knowledge_transferred": json.loads(m.knowledge_transferred) if m.knowledge_transferred else {},
        "skills_improved": json.loads(m.skills_improved) if m.skills_improved else [],
        "sessions_completed": m.sessions_completed,
        "quality_score": m.quality_score,
        "duration_days": m.duration_days,
        "status": m.status,
        "started_at": m.started_at.isoformat() if m.started_at else None,
    }
