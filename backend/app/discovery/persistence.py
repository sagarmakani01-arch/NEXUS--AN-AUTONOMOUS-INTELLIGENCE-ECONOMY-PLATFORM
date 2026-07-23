import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import and_, desc, select, func, update as sa_update

from app.core.database import async_session_factory
from app.domain.models.discovery import (
    AutomatedExperiment,
    DiscoveryArchive,
    DiscoveredPattern,
    Hypothesis,
    HypothesisValidation,
    ResearchAgent,
    ResearchLaboratory,
    ResearchReport,
    ScienceKnowledgeEdge,
    ScienceKnowledgeNode,
    ScientificExperiment,
    SimulationSnapshot,
)
# ── Scientific Experiment ──
async def create_experiment(**data) -> dict:
    async with async_session_factory() as session:
        obj = ScientificExperiment(**data)
        session.add(obj)
        await session.commit()
        return _exp_to_dict(obj)


async def update_experiment(experiment_id: str, **data) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScientificExperiment).where(ScientificExperiment.id == experiment_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        await session.commit()
        return _exp_to_dict(obj)


async def list_experiments(
    status: str | None = None, lab_type: str | None = None, limit: int = 50, offset: int = 0
) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ScientificExperiment).order_by(desc(ScientificExperiment.created_at))
        if status:
            stmt = stmt.where(ScientificExperiment.status == status)
        if lab_type:
            stmt = stmt.where(ScientificExperiment.laboratory_type == lab_type)
        stmt = stmt.offset(offset).limit(limit)
        result = await session.execute(stmt)
        return [_exp_to_dict(r) for r in result.scalars().all()]


async def get_experiment(experiment_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ScientificExperiment).where(ScientificExperiment.id == experiment_id)
        )
        obj = result.scalar_one_or_none()
        return _exp_to_dict(obj) if obj else None


# ── Automated Experiment ──
async def create_auto_experiment(**data) -> dict:
    async with async_session_factory() as session:
        obj = AutomatedExperiment(**data)
        session.add(obj)
        await session.commit()
        return _auto_exp_to_dict(obj)


async def list_auto_experiments(limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(AutomatedExperiment).order_by(desc(AutomatedExperiment.created_at)).limit(limit)
        )
        return [_auto_exp_to_dict(r) for r in result.scalars().all()]


# ── Discovered Pattern ──
async def create_pattern(**data) -> dict:
    async with async_session_factory() as session:
        obj = DiscoveredPattern(**data)
        session.add(obj)
        await session.commit()
        return _pattern_to_dict(obj)


async def list_patterns(
    pattern_type: str | None = None, min_confidence: float = 0.0, limit: int = 50
) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(DiscoveredPattern).order_by(desc(DiscoveredPattern.confidence))
        if pattern_type:
            stmt = stmt.where(DiscoveredPattern.pattern_type == pattern_type)
        stmt = stmt.where(DiscoveredPattern.confidence >= min_confidence)
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return [_pattern_to_dict(r) for r in result.scalars().all()]


async def get_pattern(pattern_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(DiscoveredPattern).where(DiscoveredPattern.id == pattern_id)
        )
        obj = result.scalar_one_or_none()
        return _pattern_to_dict(obj) if obj else None


# ── Hypothesis ──
async def create_hypothesis(**data) -> dict:
    async with async_session_factory() as session:
        obj = Hypothesis(**data)
        session.add(obj)
        await session.commit()
        return _hyp_to_dict(obj)


async def update_hypothesis(hypothesis_id: str, **data) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Hypothesis).where(Hypothesis.id == hypothesis_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        await session.commit()
        return _hyp_to_dict(obj)


async def list_hypotheses(status: str | None = None, domain: str | None = None, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Hypothesis).order_by(desc(Hypothesis.confidence_level))
        if status:
            stmt = stmt.where(Hypothesis.status == status)
        if domain:
            stmt = stmt.where(Hypothesis.domain == domain)
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return [_hyp_to_dict(r) for r in result.scalars().all()]


# ── Hypothesis Validation ──
async def create_validation(**data) -> dict:
    async with async_session_factory() as session:
        obj = HypothesisValidation(**data)
        session.add(obj)
        await session.commit()
        return _val_to_dict(obj)


async def list_validations(hypothesis_id: str | None = None, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(HypothesisValidation).order_by(desc(HypothesisValidation.created_at))
        if hypothesis_id:
            stmt = stmt.where(HypothesisValidation.hypothesis_id == hypothesis_id)
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return [_val_to_dict(r) for r in result.scalars().all()]


# ── Knowledge Graph ──
async def create_knowledge_node(**data) -> dict:
    async with async_session_factory() as session:
        obj = ScienceKnowledgeNode(**data)
        session.add(obj)
        await session.commit()
        return _node_to_dict(obj)


async def create_knowledge_edge(**data) -> dict:
    async with async_session_factory() as session:
        obj = ScienceKnowledgeEdge(**data)
        session.add(obj)
        await session.commit()
        return _edge_to_dict(obj)


async def list_knowledge_nodes(node_type: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ScienceKnowledgeNode).order_by(desc(ScienceKnowledgeNode.importance))
        if node_type:
            stmt = stmt.where(ScienceKnowledgeNode.node_type == node_type)
        result = await session.execute(stmt)
        return [_node_to_dict(r) for r in result.scalars().all()]


async def list_knowledge_edges(edge_type: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ScienceKnowledgeEdge).order_by(desc(ScienceKnowledgeEdge.weight))
        if edge_type:
            stmt = stmt.where(ScienceKnowledgeEdge.edge_type == edge_type)
        result = await session.execute(stmt)
        return [_edge_to_dict(r) for r in result.scalars().all()]


# ── Laboratory ──
async def create_laboratory(**data) -> dict:
    async with async_session_factory() as session:
        obj = ResearchLaboratory(**data)
        session.add(obj)
        await session.commit()
        return _lab_to_dict(obj)


async def list_laboratories(lab_type: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ResearchLaboratory).order_by(ResearchLaboratory.name)
        if lab_type:
            stmt = stmt.where(ResearchLaboratory.lab_type == lab_type)
        result = await session.execute(stmt)
        return [_lab_to_dict(r) for r in result.scalars().all()]


async def get_laboratory(lab_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ResearchLaboratory).where(ResearchLaboratory.id == lab_id)
        )
        obj = result.scalar_one_or_none()
        return _lab_to_dict(obj) if obj else None


async def update_laboratory(lab_id: str, **data) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ResearchLaboratory).where(ResearchLaboratory.id == lab_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        await session.commit()
        return _lab_to_dict(obj)


# ── Research Agent ──
async def create_research_agent(**data) -> dict:
    async with async_session_factory() as session:
        obj = ResearchAgent(**data)
        session.add(obj)
        await session.commit()
        return _rag_to_dict(obj)


async def list_research_agents(specialization: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ResearchAgent).order_by(ResearchAgent.name)
        if specialization:
            stmt = stmt.where(ResearchAgent.specialization == specialization)
        result = await session.execute(stmt)
        return [_rag_to_dict(r) for r in result.scalars().all()]


async def update_research_agent(agent_id: str, **data) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ResearchAgent).where(ResearchAgent.id == agent_id)
        )
        obj = result.scalar_one_or_none()
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        await session.commit()
        return _rag_to_dict(obj)


# ── Research Report ──
async def create_report(**data) -> dict:
    async with async_session_factory() as session:
        obj = ResearchReport(**data)
        session.add(obj)
        await session.commit()
        return _rep_to_dict(obj)


async def list_reports(limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ResearchReport).order_by(desc(ResearchReport.created_at)).limit(limit)
        )
        return [_rep_to_dict(r) for r in result.scalars().all()]


async def get_report(report_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(ResearchReport).where(ResearchReport.id == report_id)
        )
        obj = result.scalar_one_or_none()
        return _rep_to_dict(obj) if obj else None


# ── Archive ──
async def create_archive_entry(**data) -> dict:
    async with async_session_factory() as session:
        obj = DiscoveryArchive(**data)
        session.add(obj)
        await session.commit()
        return _arch_to_dict(obj)


async def list_archive(archive_type: str | None = None, limit: int = 100) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(DiscoveryArchive).order_by(desc(DiscoveryArchive.created_at))
        if archive_type:
            stmt = stmt.where(DiscoveryArchive.archive_type == archive_type)
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return [_arch_to_dict(r) for r in result.scalars().all()]


# ── Snapshot ──
async def create_snapshot(**data) -> dict:
    async with async_session_factory() as session:
        obj = SimulationSnapshot(**data)
        session.add(obj)
        await session.commit()
        return _snap_to_dict(obj)


async def get_snapshots(
    snapshot_type: str | None = None,
    metric_name: str | None = None,
    limit: int = 200,
) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(SimulationSnapshot).order_by(desc(SimulationSnapshot.tick))
        if snapshot_type:
            stmt = stmt.where(SimulationSnapshot.snapshot_type == snapshot_type)
        if metric_name:
            stmt = stmt.where(SimulationSnapshot.metric_name == metric_name)
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        return [_snap_to_dict(r) for r in result.scalars().all()]


# ── Stats ──
async def get_discovery_stats() -> dict:
    async with async_session_factory() as session:
        exp_count = (await session.execute(select(func.count(ScientificExperiment.id)))).scalar()
        pat_count = (await session.execute(select(func.count(DiscoveredPattern.id)))).scalar()
        hyp_count = (await session.execute(select(func.count(Hypothesis.id)))).scalar()
        rep_count = (await session.execute(select(func.count(ResearchReport.id)))).scalar()
        arch_count = (await session.execute(select(func.count(DiscoveryArchive.id)))).scalar()
        lab_count = (await session.execute(select(func.count(ResearchLaboratory.id)))).scalar()
        rag_count = (await session.execute(select(func.count(ResearchAgent.id)))).scalar()
        snap_count = (await session.execute(select(func.count(SimulationSnapshot.id)))).scalar()
        return {
            "experiments": exp_count or 0,
            "patterns": pat_count or 0,
            "hypotheses": hyp_count or 0,
            "reports": rep_count or 0,
            "archives": arch_count or 0,
            "laboratories": lab_count or 0,
            "research_agents": rag_count or 0,
            "snapshots": snap_count or 0,
        }


def _parse_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


def _exp_to_dict(obj: ScientificExperiment) -> dict:
    return {
        "id": obj.id,
        "title": obj.title,
        "research_question": obj.research_question,
        "hypothesis": obj.hypothesis,
        "variables": _parse_json(obj.variables),
        "constraints": _parse_json(obj.constraints),
        "simulation_params": _parse_json(obj.simulation_params),
        "duration_ticks": obj.duration_ticks,
        "status": obj.status,
        "result_summary": obj.result_summary,
        "confidence_score": obj.confidence_score,
        "created_by": obj.created_by,
        "laboratory_type": obj.laboratory_type,
        "tags": _parse_json(obj.tags),
        "started_at": obj.started_at.isoformat() if obj.started_at else None,
        "completed_at": obj.completed_at.isoformat() if obj.completed_at else None,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _auto_exp_to_dict(obj: AutomatedExperiment) -> dict:
    return {
        "id": obj.id,
        "trigger_observation": obj.trigger_observation,
        "experiment_type": obj.experiment_type,
        "variable_name": obj.variable_name,
        "variable_change": obj.variable_change,
        "duration_ticks": obj.duration_ticks,
        "status": obj.status,
        "result_summary": obj.result_summary,
        "significance": obj.significance,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _pattern_to_dict(obj: DiscoveredPattern) -> dict:
    return {
        "id": obj.id,
        "pattern_type": obj.pattern_type,
        "title": obj.title,
        "description": obj.description,
        "antecedent": obj.antecedent,
        "consequent": obj.consequent,
        "confidence": obj.confidence,
        "support": obj.support,
        "lift": obj.lift,
        "sample_size": obj.sample_size,
        "method": obj.method,
        "tags": _parse_json(obj.tags),
        "status": obj.status,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _hyp_to_dict(obj: Hypothesis) -> dict:
    return {
        "id": obj.id,
        "title": obj.title,
        "description": obj.description,
        "phenomenon": obj.phenomenon,
        "proposed_explanation": obj.proposed_explanation,
        "supporting_evidence": _parse_json(obj.supporting_evidence),
        "counterexamples": _parse_json(obj.counterexamples),
        "confidence_level": obj.confidence_level,
        "status": obj.status,
        "domain": obj.domain,
        "created_by": obj.created_by,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _val_to_dict(obj: HypothesisValidation) -> dict:
    return {
        "id": obj.id,
        "hypothesis_id": obj.hypothesis_id,
        "experiment_id": obj.experiment_id,
        "validation_type": obj.validation_type,
        "outcome": obj.outcome,
        "confidence_delta": obj.confidence_delta,
        "notes": obj.notes,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _node_to_dict(obj: ScienceKnowledgeNode) -> dict:
    return {
        "id": obj.id,
        "node_type": obj.node_type,
        "name": obj.name,
        "description": obj.description,
        "data": _parse_json(obj.data),
        "importance": obj.importance,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _edge_to_dict(obj: ScienceKnowledgeEdge) -> dict:
    return {
        "id": obj.id,
        "source_node_id": obj.source_node_id,
        "target_node_id": obj.target_node_id,
        "edge_type": obj.edge_type,
        "weight": obj.weight,
        "description": obj.description,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _lab_to_dict(obj: ResearchLaboratory) -> dict:
    return {
        "id": obj.id,
        "name": obj.name,
        "lab_type": obj.lab_type,
        "description": obj.description,
        "specialization": _parse_json(obj.specialization),
        "experiment_count": obj.experiment_count,
        "active": bool(obj.active),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _rag_to_dict(obj: ResearchAgent) -> dict:
    return {
        "id": obj.id,
        "name": obj.name,
        "specialization": obj.specialization,
        "laboratory_id": obj.laboratory_id,
        "experiments_conducted": obj.experiments_conducted,
        "patterns_discovered": obj.patterns_discovered,
        "reports_written": obj.reports_written,
        "accuracy_score": obj.accuracy_score,
        "status": obj.status,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _rep_to_dict(obj: ResearchReport) -> dict:
    return {
        "id": obj.id,
        "title": obj.title,
        "research_question": obj.research_question,
        "methodology": obj.methodology,
        "simulation_setup": obj.simulation_setup,
        "results": obj.results,
        "limitations": obj.limitations,
        "future_experiments": obj.future_experiments,
        "confidence_score": obj.confidence_score,
        "status": obj.status,
        "created_by_agent_id": obj.created_by_agent_id,
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _arch_to_dict(obj: DiscoveryArchive) -> dict:
    return {
        "id": obj.id,
        "archive_type": obj.archive_type,
        "title": obj.title,
        "content": obj.content,
        "reference_id": obj.reference_id,
        "success": bool(obj.success),
        "tags": _parse_json(obj.tags),
        "created_at": obj.created_at.isoformat() if obj.created_at else None,
    }


def _snap_to_dict(obj: SimulationSnapshot) -> dict:
    return {
        "id": obj.id,
        "snapshot_type": obj.snapshot_type,
        "metric_name": obj.metric_name,
        "metric_value": obj.metric_value,
        "tick": obj.tick,
        "civilization_id": obj.civilization_id,
        "metadata_json": _parse_json(obj.metadata_json),
        "recorded_at": obj.recorded_at.isoformat() if obj.recorded_at else None,
    }
