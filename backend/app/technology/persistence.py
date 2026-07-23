import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.technology import (
    Technology, TechnologyEdge, TechnologyDiscovery, TechnologyDevelopment,
    TechnologyAdoption, ScientificOrganization, Scientist,
    CivilizationTechLevel, TechnologyTimeline,
)

logger = logging.getLogger("nexus.technology.persistence")


async def create_technology(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = Technology(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def get_technology(tech_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(Technology).where(Technology.id == tech_id))
        o = r.scalar_one_or_none()
        return _tech_to_dict(o) if o else None


async def list_technologies(domain: str | None = None, status: str | None = None,
                            civ_id: str | None = None, limit: int = 100) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Technology)
        conds = []
        if domain:
            conds.append(Technology.domain == domain)
        if status:
            conds.append(Technology.status == status)
        if civ_id:
            conds.append(Technology.origin_civilization_id == civ_id)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(Technology.impact_score.desc()).limit(limit)
        r = await session.execute(stmt)
        return [_tech_to_dict(t) for t in r.scalars().all()]


async def update_technology(tech_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(Technology).where(Technology.id == tech_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_technology_edge(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = TechnologyEdge(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_technology_edges(source_id: str | None = None, target_id: str | None = None,
                                edge_type: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(TechnologyEdge)
        conds = []
        if source_id:
            conds.append(TechnologyEdge.source_technology_id == source_id)
        if target_id:
            conds.append(TechnologyEdge.target_technology_id == target_id)
        if edge_type:
            conds.append(TechnologyEdge.edge_type == edge_type)
        if conds:
            stmt = stmt.where(and_(*conds))
        r = await session.execute(stmt)
        return [
            {"id": e.id, "source_technology_id": e.source_technology_id,
             "target_technology_id": e.target_technology_id,
             "edge_type": e.edge_type, "weight": e.weight,
             "description": e.description,
             "created_at": e.created_at.isoformat() if e.created_at else None}
            for e in r.scalars().all()
        ]


async def create_discovery(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = TechnologyDiscovery(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_discoveries(civ_id: str | None = None, status: str | None = None,
                           limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(TechnologyDiscovery)
        conds = []
        if civ_id:
            conds.append(TechnologyDiscovery.civilization_id == civ_id)
        if status:
            conds.append(TechnologyDiscovery.status == status)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(TechnologyDiscovery.impact_score.desc()).limit(limit)
        r = await session.execute(stmt)
        return [_disc_to_dict(d) for d in r.scalars().all()]


async def update_discovery(disc_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(TechnologyDiscovery).where(TechnologyDiscovery.id == disc_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await session.commit()


async def create_development(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = TechnologyDevelopment(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_developments(civ_id: str | None = None, tech_id: str | None = None,
                            status: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(TechnologyDevelopment)
        conds = []
        if civ_id:
            conds.append(TechnologyDevelopment.civilization_id == civ_id)
        if tech_id:
            conds.append(TechnologyDevelopment.technology_id == tech_id)
        if status:
            conds.append(TechnologyDevelopment.status == status)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(TechnologyDevelopment.created_at.desc())
        r = await session.execute(stmt)
        return [_dev_to_dict(d) for d in r.scalars().all()]


async def update_development(dev_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(TechnologyDevelopment).where(TechnologyDevelopment.id == dev_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_adoption(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = TechnologyAdoption(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_adoptions(civ_id: str | None = None, tech_id: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(TechnologyAdoption)
        conds = []
        if civ_id:
            conds.append(TechnologyAdoption.civilization_id == civ_id)
        if tech_id:
            conds.append(TechnologyAdoption.technology_id == tech_id)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(TechnologyAdoption.decided_at.desc())
        r = await session.execute(stmt)
        return [
            {"id": a.id, "civilization_id": a.civilization_id,
             "technology_id": a.technology_id, "decision": a.decision,
             "economic_benefit": a.economic_benefit, "cost": a.cost,
             "risk": a.risk, "cultural_compatibility": a.cultural_compatibility,
             "strategic_importance": a.strategic_importance,
             "decided_at": a.decided_at.isoformat() if a.decided_at else None}
            for a in r.scalars().all()
        ]


async def create_scientific_organization(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = ScientificOrganization(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_scientific_organizations(civ_id: str | None = None,
                                        org_type: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ScientificOrganization)
        conds = []
        if civ_id:
            conds.append(ScientificOrganization.civilization_id == civ_id)
        if org_type:
            conds.append(ScientificOrganization.org_type == org_type)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(ScientificOrganization.reputation.desc())
        r = await session.execute(stmt)
        return [_org_to_dict(o) for o in r.scalars().all()]


async def update_scientific_organization(org_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(ScientificOrganization).where(ScientificOrganization.id == org_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_scientist(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = Scientist(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_scientists(civ_id: str | None = None,
                          org_id: str | None = None,
                          specialization: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Scientist)
        conds = []
        if civ_id:
            conds.append(Scientist.civilization_id == civ_id)
        if org_id:
            conds.append(Scientist.organization_id == org_id)
        if specialization:
            conds.append(Scientist.specialization == specialization)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(Scientist.influence_score.desc())
        r = await session.execute(stmt)
        return [_scientist_to_dict(s) for s in r.scalars().all()]


async def update_scientist(sci_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(Scientist).where(Scientist.id == sci_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def get_tech_level(civ_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationTechLevel).where(CivilizationTechLevel.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        return _techlevel_to_dict(o) if o else None


async def create_tech_level(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = CivilizationTechLevel(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def update_tech_level(civ_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationTechLevel).where(CivilizationTechLevel.civilization_id == civ_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.last_calculated = datetime.now(timezone.utc)
            await session.commit()


async def create_timeline_event(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = TechnologyTimeline(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_timeline(civ_id: str | None = None,
                        event_type: str | None = None,
                        limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(TechnologyTimeline)
        conds = []
        if civ_id:
            conds.append(TechnologyTimeline.civilization_id == civ_id)
        if event_type:
            conds.append(TechnologyTimeline.event_type == event_type)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(TechnologyTimeline.recorded_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": t.id, "civilization_id": t.civilization_id,
             "event_type": t.event_type, "technology_id": t.technology_id,
             "title": t.title, "description": t.description,
             "impact_score": t.impact_score,
             "recorded_at": t.recorded_at.isoformat() if t.recorded_at else None}
            for t in r.scalars().all()
        ]


async def get_tech_stats() -> dict:
    async with async_session_factory() as session:
        techs = await session.execute(select(func.count(Technology.id)))
        edges = await session.execute(select(func.count(TechnologyEdge.id)))
        discs = await session.execute(select(func.count(TechnologyDiscovery.id)))
        orgs = await session.execute(select(func.count(ScientificOrganization.id)))
        scis = await session.execute(select(func.count(Scientist.id)))
        return {
            "technologies": techs.scalar() or 0,
            "technology_edges": edges.scalar() or 0,
            "discoveries": discs.scalar() or 0,
            "scientific_organizations": orgs.scalar() or 0,
            "scientists": scis.scalar() or 0,
        }


def _tech_to_dict(o) -> dict:
    return {
        "id": o.id, "name": o.name, "domain": o.domain,
        "description": o.description, "tech_type": o.tech_type,
        "origin_civilization_id": o.origin_civilization_id,
        "discovery_date": o.discovery_date.isoformat() if o.discovery_date else None,
        "required_knowledge": json.loads(o.required_knowledge) if o.required_knowledge else [],
        "required_resources": json.loads(o.required_resources) if o.required_resources else {},
        "difficulty_level": o.difficulty_level, "impact_score": o.impact_score,
        "current_level": o.current_level,
        "applications": json.loads(o.applications) if o.applications else [],
        "prerequisites": json.loads(o.prerequisites) if o.prerequisites else [],
        "maturity": o.maturity, "adoption_count": o.adoption_count,
        "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _disc_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "technology_id": o.technology_id, "title": o.title,
        "description": o.description, "difficulty": o.difficulty,
        "impact_score": o.impact_score, "discoverer_agent_id": o.discoverer_agent_id,
        "method": o.method, "confidence": o.confidence, "status": o.status,
        "discovered_at": o.discovered_at.isoformat() if o.discovered_at else None,
    }


def _dev_to_dict(o) -> dict:
    return {
        "id": o.id, "technology_id": o.technology_id,
        "civilization_id": o.civilization_id, "stage": o.stage,
        "progress": o.progress, "resource_cost": o.resource_cost,
        "time_spent": o.time_spent, "lead_agent_id": o.lead_agent_id,
        "team_agent_ids": json.loads(o.team_agent_ids) if o.team_agent_ids else [],
        "notes": o.notes, "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _org_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "name": o.name, "org_type": o.org_type,
        "description": o.description, "research_output": o.research_output,
        "discoveries_count": o.discoveries_count,
        "scientist_count": o.scientist_count,
        "funding_level": o.funding_level, "reputation": o.reputation,
        "specialization": json.loads(o.specialization) if o.specialization else [],
        "active": o.active,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _scientist_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "agent_id": o.agent_id, "name": o.name,
        "specialization": o.specialization,
        "organization_id": o.organization_id,
        "research_output": o.research_output,
        "discoveries_count": o.discoveries_count,
        "publications_count": o.publications_count,
        "influence_score": o.influence_score, "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _techlevel_to_dict(o) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "computational_capability": o.computational_capability,
        "energy_capability": o.energy_capability,
        "manufacturing_capability": o.manufacturing_capability,
        "scientific_knowledge": o.scientific_knowledge,
        "automation_level": o.automation_level,
        "infrastructure_level": o.infrastructure_level,
        "current_era": o.current_era,
        "last_calculated": o.last_calculated.isoformat() if o.last_calculated else None,
    }
