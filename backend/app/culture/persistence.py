import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.culture import (
    CulturalIdentity, ValueSystem, Institution, Tradition,
    CivilizationCommunity, CommunityMembership, CollectiveMemory,
    SocialDynamics, ReputationEntry, CulturalTimeline, CivilizationIdentityScore,
)

logger = logging.getLogger("nexus.culture.persistence")


async def create_cultural_identity(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = CulturalIdentity(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def get_cultural_identity(civ_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(CulturalIdentity).where(CulturalIdentity.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        return _identity_to_dict(o) if o else None


async def update_cultural_identity(civ_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(CulturalIdentity).where(CulturalIdentity.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_value_system(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = ValueSystem(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def get_value_system(civ_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(ValueSystem).where(ValueSystem.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        return _values_to_dict(o) if o else None


async def update_value_system(civ_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(ValueSystem).where(ValueSystem.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_institution(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = Institution(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_institutions(civ_id: str | None = None, inst_type: str | None = None,
                            active: bool = True) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Institution)
        conds = []
        if civ_id:
            conds.append(Institution.civilization_id == civ_id)
        if inst_type:
            conds.append(Institution.institution_type == inst_type)
        if active is not None:
            conds.append(Institution.active == active)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(Institution.influence.desc())
        r = await session.execute(stmt)
        return [_inst_to_dict(i) for i in r.scalars().all()]


async def get_institution(inst_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(Institution).where(Institution.id == inst_id))
        o = r.scalar_one_or_none()
        return _inst_to_dict(o) if o else None


async def update_institution(inst_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(Institution).where(Institution.id == inst_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_tradition(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = Tradition(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_traditions(civ_id: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Tradition)
        if civ_id:
            stmt = stmt.where(Tradition.civilization_id == civ_id)
        stmt = stmt.order_by(Tradition.impact_score.desc())
        r = await session.execute(stmt)
        return [_trad_to_dict(t) for t in r.scalars().all()]


async def update_tradition(trad_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(Tradition).where(Tradition.id == trad_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_community(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = CivilizationCommunity(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_communities(civ_id: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(CivilizationCommunity)
        if civ_id:
            stmt = stmt.where(CivilizationCommunity.civilization_id == civ_id)
        stmt = stmt.order_by(CivilizationCommunity.member_count.desc())
        r = await session.execute(stmt)
        return [_comm_to_dict(c) for c in r.scalars().all()]


async def get_community(comm_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationCommunity).where(CivilizationCommunity.id == comm_id))
        o = r.scalar_one_or_none()
        return _comm_to_dict(o) if o else None


async def update_community(comm_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationCommunity).where(CivilizationCommunity.id == comm_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_community_membership(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = CommunityMembership(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_community_members(community_id: str) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(CommunityMembership).where(CommunityMembership.community_id == community_id)
        r = await session.execute(stmt)
        return [
            {"id": m.id, "community_id": m.community_id, "entity_id": m.entity_id,
             "entity_type": m.entity_type, "role": m.role,
             "contribution_score": m.contribution_score,
             "joined_at": m.joined_at.isoformat() if m.joined_at else None}
            for m in r.scalars().all()
        ]


async def create_collective_memory(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = CollectiveMemory(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_collective_memories(civ_id: str | None = None,
                                   event_type: str | None = None,
                                   limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(CollectiveMemory)
        conds = []
        if civ_id:
            conds.append(CollectiveMemory.civilization_id == civ_id)
        if event_type:
            conds.append(CollectiveMemory.event_type == event_type)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(CollectiveMemory.impact_score.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": m.id, "civilization_id": m.civilization_id, "event_type": m.event_type,
             "title": m.title, "description": m.description,
             "impact_score": m.impact_score,
             "recorded_at": m.recorded_at.isoformat() if m.recorded_at else None}
            for m in r.scalars().all()
        ]


async def create_social_dynamics(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = SocialDynamics(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def get_social_dynamics(civ_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(SocialDynamics).where(SocialDynamics.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        return _dynamics_to_dict(o) if o else None


async def update_social_dynamics(civ_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(SocialDynamics).where(SocialDynamics.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_reputation_entry(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = ReputationEntry(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_reputation_entries(civ_id: str | None = None,
                                  entity_type: str | None = None,
                                  limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ReputationEntry)
        conds = []
        if civ_id:
            conds.append(ReputationEntry.civilization_id == civ_id)
        if entity_type:
            conds.append(ReputationEntry.entity_type == entity_type)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(ReputationEntry.influence_score.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": e.id, "civilization_id": e.civilization_id, "entity_id": e.entity_id,
             "entity_type": e.entity_type, "influence_score": e.influence_score,
             "contribution_count": e.contribution_count,
             "sustained_engagement": e.sustained_engagement,
             "last_updated": e.last_updated.isoformat() if e.last_updated else None}
            for e in r.scalars().all()
        ]


async def create_cultural_timeline(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = CulturalTimeline(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_cultural_timeline(civ_id: str | None = None,
                                 change_type: str | None = None,
                                 limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(CulturalTimeline)
        conds = []
        if civ_id:
            conds.append(CulturalTimeline.civilization_id == civ_id)
        if change_type:
            conds.append(CulturalTimeline.change_type == change_type)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(CulturalTimeline.recorded_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": t.id, "civilization_id": t.civilization_id, "change_type": t.change_type,
             "description": t.description, "cause": t.cause,
             "impact_score": t.impact_score,
             "recorded_at": t.recorded_at.isoformat() if t.recorded_at else None}
            for t in r.scalars().all()
        ]


async def create_identity_score(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = CivilizationIdentityScore(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def get_identity_score(civ_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationIdentityScore).where(CivilizationIdentityScore.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        return _score_to_dict(o) if o else None


async def update_identity_score(civ_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationIdentityScore).where(CivilizationIdentityScore.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.last_calculated = datetime.now(timezone.utc)
            await session.commit()


async def get_culture_stats() -> dict:
    async with async_session_factory() as session:
        ids = await session.execute(select(func.count(CulturalIdentity.id)))
        insts = await session.execute(select(func.count(Institution.id)))
        trads = await session.execute(select(func.count(Tradition.id)))
        comms = await session.execute(select(func.count(CivilizationCommunity.id)))
        mems = await session.execute(select(func.count(CollectiveMemory.id)))
        timelines = await session.execute(select(func.count(CulturalTimeline.id)))
        return {
            "cultural_identities": ids.scalar() or 0,
            "institutions": insts.scalar() or 0,
            "traditions": trads.scalar() or 0,
            "communities": comms.scalar() or 0,
            "collective_memories": mems.scalar() or 0,
            "timeline_events": timelines.scalar() or 0,
        }


def _identity_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id, "name": o.name,
        "core_values": json.loads(o.core_values) if o.core_values else {},
        "shared_history": json.loads(o.shared_history) if o.shared_history else [],
        "social_norms": json.loads(o.social_norms) if o.social_norms else [],
        "historical_symbols": json.loads(o.historical_symbols) if o.historical_symbols else [],
        "long_term_goals": json.loads(o.long_term_goals) if o.long_term_goals else [],
        "identity_strength": o.identity_strength,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _values_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "innovation": o.innovation, "cooperation": o.cooperation,
        "competition": o.competition, "education": o.education,
        "efficiency": o.efficiency, "sustainability": o.sustainability,
        "exploration": o.exploration, "security": o.security,
        "transparency": o.transparency,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _inst_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "name": o.name, "institution_type": o.institution_type,
        "description": o.description,
        "strength": o.strength, "influence": o.influence,
        "membership_count": o.membership_count, "active": o.active,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _trad_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "name": o.name, "description": o.description,
        "frequency": o.frequency, "impact_score": o.impact_score,
        "last_held": o.last_held.isoformat() if o.last_held else None,
        "next_held": o.next_held.isoformat() if o.next_held else None,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _comm_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "name": o.name, "description": o.description,
        "community_type": o.community_type,
        "member_count": o.member_count, "growth_rate": o.growth_rate,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _dynamics_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "collaboration_score": o.collaboration_score,
        "competition_score": o.competition_score,
        "trust_level": o.trust_level,
        "influence_distribution": json.loads(o.influence_distribution) if o.influence_distribution else {},
        "knowledge_sharing_score": o.knowledge_sharing_score,
        "community_growth_rate": o.community_growth_rate,
        "updated_at": o.updated_at.isoformat() if o.updated_at else None,
    }


def _score_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "knowledge_orientation": o.knowledge_orientation,
        "innovation_orientation": o.innovation_orientation,
        "economic_stability": o.economic_stability,
        "social_cohesion": o.social_cohesion,
        "institutional_strength": o.institutional_strength,
        "adaptability": o.adaptability,
        "last_calculated": o.last_calculated.isoformat() if o.last_calculated else None,
    }
