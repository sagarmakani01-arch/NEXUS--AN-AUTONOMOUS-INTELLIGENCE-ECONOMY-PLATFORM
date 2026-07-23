import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.research import ResearchOrganization, ResearchProject, KnowledgeNode, KnowledgeEdge

logger = logging.getLogger("nexus.research.persistence")


async def create_technology(**kwargs) -> str:
    async with async_session_factory() as session:
        t = ResearchOrganization(**kwargs)
        session.add(t)
        await session.commit()
        return t.id


async def list_technologies(domain: str | None = None, status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ResearchOrganization).where(ResearchOrganization.status == status)
        if domain:
            stmt = stmt.where(ResearchOrganization.org_type == domain)
        stmt = stmt.order_by(ResearchOrganization.reputation.desc())
        r = await session.execute(stmt)
        return [_org_to_dict(o) for o in r.scalars().all()]


async def get_technology(tech_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(ResearchOrganization).where(ResearchOrganization.id == tech_id))
        o = r.scalar_one_or_none()
        return _org_to_dict(o) if o else None


async def update_technology(tech_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(ResearchOrganization).where(ResearchOrganization.id == tech_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_discovery(**kwargs) -> str:
    pass


async def list_discoveries(civ_id: str | None = None) -> list[dict]:
    pass


async def create_knowledge_node(**kwargs) -> str:
    async with async_session_factory() as session:
        n = KnowledgeNode(**kwargs)
        session.add(n)
        await session.commit()
        return n.id


async def list_knowledge_nodes(position_x: float | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(KnowledgeNode)
        if position_x is not None:
            stmt = stmt.where(KnowledgeNode.position_x == position_x)
        r = await session.execute(stmt)
        return [_node_to_dict(n) for n in r.scalars().all()]


async def update_knowledge_node(node_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(KnowledgeNode).where(KnowledgeNode.id == node_id))
        n = r.scalar_one_or_none()
        if n:
            for k, v in kwargs.items():
                if hasattr(n, k):
                    setattr(n, k, v)
            n.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_knowledge_edge(**kwargs) -> str:
    async with async_session_factory() as session:
        e = KnowledgeEdge(**kwargs)
        session.add(e)
        await session.commit()
        return e.id


async def list_knowledge_edges(source_node_id: str | None = None,
                               target_node_id: str | None = None,
                               edge_type: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(KnowledgeEdge)
        conds = []
        if source_node_id:
            conds.append(KnowledgeEdge.source_node_id == source_node_id)
        if target_node_id:
            conds.append(KnowledgeEdge.target_node_id == target_node_id)
        if edge_type:
            conds.append(KnowledgeEdge.edge_type == edge_type)
        if conds:
            stmt = stmt.where(and_(*conds))
        r = await session.execute(stmt)
        return [
            {"id": e.id, "source_node_id": e.source_node_id, "target_node_id": e.target_node_id,
             "edge_type": e.edge_type, "weight": e.weight, "description": e.description,
             "confidence": e.confidence, "created_by_agent_id": e.created_by_agent_id,
             "created_at": e.created_at.isoformat() if e.created_at else None}
            for e in r.scalars().all()
        ]


async def create_project(**kwargs) -> str:
    async with async_session_factory() as session:
        p = ResearchProject(**kwargs)
        session.add(p)
        await session.commit()
        return p.id


async def list_projects(organization_id: str | None = None, status: str | None = None,
                        limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ResearchProject)
        conds = []
        if organization_id:
            conds.append(ResearchProject.organization_id == organization_id)
        if status:
            conds.append(ResearchProject.status == status)
        if conds:
            stmt = stmt.where(and_(*conds))
        stmt = stmt.order_by(ResearchProject.created_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [_proj_to_dict(p) for p in r.scalars().all()]


async def create_scientist(**kwargs) -> str:
    pass


async def list_scientists(domain: str | None = None) -> list[dict]:
    pass


async def create_adoption_decision(**kwargs) -> str:
    pass


async def list_adoptions(civ_id: str | None = None) -> list[dict]:
    pass


async def get_research_stats() -> dict:
    async with async_session_factory() as session:
        orgs = await session.execute(select(func.count(ResearchOrganization.id)))
        projects = await session.execute(select(func.count(ResearchProject.id)))
        nodes = await session.execute(select(func.count(KnowledgeNode.id)))
        edges = await session.execute(select(func.count(KnowledgeEdge.id)))
        return {
            "organizations": orgs.scalar() or 0,
            "projects": projects.scalar() or 0,
            "knowledge_nodes": nodes.scalar() or 0,
            "knowledge_edges": edges.scalar() or 0,
        }


def _org_to_dict(o) -> dict:
    return {
        "id": o.id, "name": o.name, "org_type": o.org_type,
        "description": o.description, "founder_agent_id": o.founder_agent_id,
        "research_budget": o.research_budget, "reputation": o.reputation,
        "research_areas": json.loads(o.research_areas) if o.research_areas else [],
        "scientist_agent_ids": json.loads(o.scientist_agent_ids) if o.scientist_agent_ids else [],
        "total_projects": o.total_projects, "completed_projects": o.completed_projects,
        "published_papers": o.published_papers, "citations_received": o.citations_received,
        "technologies_developed": json.loads(o.technologies_developed) if o.technologies_developed else [],
        "knowledge_nodes_created": o.knowledge_nodes_created,
        "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _node_to_dict(n) -> dict:
    return {
        "id": n.id, "name": n.name, "node_type": n.node_type,
        "description": n.description, "domain": n.domain,
        "maturity_level": n.maturity_level, "confidence": n.confidence,
        "novelty_score": n.novelty_score, "utility_score": n.utility_score,
        "citations": n.citations, "usage_count": n.usage_count,
        "keywords": json.loads(n.keywords) if n.keywords else [],
        "status": n.status,
        "created_at": n.created_at.isoformat() if n.created_at else None,
        "position_x": n.position_x,
        "position_y": n.position_y,
    }


def _proj_to_dict(p) -> dict:
    return {
        "id": p.id, "organization_id": p.organization_id,
        "lead_agent_id": p.lead_agent_id, "title": p.title,
        "research_question": p.research_question, "hypothesis": p.hypothesis,
        "objectives": json.loads(p.objectives) if p.objectives else [],
        "required_skills": json.loads(p.required_skills) if p.required_skills else [],
        "budget": p.budget, "budget_spent": p.budget_spent,
        "timeline_days": p.timeline_days, "days_elapsed": p.days_elapsed,
        "status": p.status, "priority": p.priority,
        "dependencies": json.loads(p.dependencies) if p.dependencies else [],
        "expected_impact": p.expected_impact, "actual_impact": p.actual_impact,
        "progress": p.progress, "team_agent_ids": json.loads(p.team_agent_ids) if p.team_agent_ids else [],
        "knowledge_domain": p.knowledge_domain, "funding_source": p.funding_source,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }
