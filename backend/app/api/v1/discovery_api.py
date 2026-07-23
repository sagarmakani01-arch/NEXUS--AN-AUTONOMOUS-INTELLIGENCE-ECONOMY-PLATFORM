from fastapi import APIRouter, HTTPException

from app.discovery import persistence as db
from app.discovery.engine import discovery_engine
from app.discovery.experiment_framework import create_controlled_experiment, run_experiment, compare_experiments
from app.discovery.hypothesis_generator import generate_hypothesis_from_pattern
from app.discovery.knowledge_graph import get_knowledge_graph, search_discoveries
from app.discovery.report_generator import generate_report
from app.discovery.validation import validate_hypothesis

router = APIRouter(prefix="/api/v1/discovery", tags=["discovery"])


# ── Experiments ──
@router.post("/experiments")
async def api_create_experiment(data: dict):
    exp = await create_controlled_experiment(
        title=data.get("title", "Untitled"),
        research_question=data.get("research_question"),
        hypothesis=data.get("hypothesis"),
        variables=data.get("variables"),
        constraints=data.get("constraints"),
        simulation_params=data.get("simulation_params"),
        duration_ticks=data.get("duration_ticks", 100),
        laboratory_type=data.get("laboratory_type", "general"),
        created_by=data.get("created_by"),
        tags=data.get("tags"),
    )
    return exp


@router.post("/experiments/{experiment_id}/run")
async def api_run_experiment(experiment_id: str):
    result = await run_experiment(experiment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result


@router.get("/experiments")
async def api_list_experiments(
    status: str | None = None,
    lab_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    return await db.list_experiments(status=status, lab_type=lab_type, limit=limit, offset=offset)


@router.get("/experiments/{experiment_id}")
async def api_get_experiment(experiment_id: str):
    exp = await db.get_experiment(experiment_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return exp


@router.post("/experiments/compare")
async def api_compare_experiments(data: dict):
    ids = data.get("experiment_ids", [])
    return await compare_experiments(ids)


# ── Automated Experiments ──
@router.post("/auto-experiments")
async def api_create_auto_experiment():
    from app.discovery.auto_experiment import generate_experiment
    return await generate_experiment()


@router.get("/auto-experiments")
async def api_list_auto_experiments(limit: int = 50):
    return await db.list_auto_experiments(limit=limit)


# ── Patterns ──
@router.get("/patterns")
async def api_list_patterns(
    pattern_type: str | None = None,
    min_confidence: float = 0.0,
    limit: int = 50,
):
    return await db.list_patterns(pattern_type=pattern_type, min_confidence=min_confidence, limit=limit)


@router.get("/patterns/{pattern_id}")
async def api_get_pattern(pattern_id: str):
    pattern = await db.get_pattern(pattern_id)
    if not pattern:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return pattern


# ── Hypotheses ──
@router.get("/hypotheses")
async def api_list_hypotheses(
    status: str | None = None,
    domain: str | None = None,
    limit: int = 50,
):
    return await db.list_hypotheses(status=status, domain=domain, limit=limit)


@router.get("/hypotheses/{hypothesis_id}")
async def api_get_hypothesis(hypothesis_id: str):
    hyp = await db.get_hypothesis(hypothesis_id)
    if not hyp:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return hyp


@router.post("/hypotheses/{hypothesis_id}/validate")
async def api_validate_hypothesis(hypothesis_id: str):
    result = await validate_hypothesis(hypothesis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Hypothesis not found")
    return result


@router.post("/hypotheses/generate-from-pattern/{pattern_id}")
async def api_generate_hypothesis_from_pattern(pattern_id: str):
    hypothesis = await generate_hypothesis_from_pattern(pattern_id)
    if not hypothesis:
        raise HTTPException(status_code=404, detail="Pattern not found")
    return hypothesis


# ── Knowledge Graph ──
@router.get("/knowledge")
async def api_get_knowledge_graph(
    node_type: str | None = None,
    edge_type: str | None = None,
):
    return await get_knowledge_graph(node_type=node_type, edge_type=edge_type)


@router.get("/knowledge/search")
async def api_search_discoveries(query: str):
    return await search_discoveries(query)


# ── Laboratories ──
@router.get("/laboratories")
async def api_list_laboratories(lab_type: str | None = None):
    return await db.list_laboratories(lab_type=lab_type)


@router.get("/laboratories/{lab_id}")
async def api_get_laboratory(lab_id: str):
    lab = await db.get_laboratory(lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Laboratory not found")
    return lab


@router.post("/laboratories/{lab_id}/run")
async def api_run_lab_experiment(lab_id: str, data: dict | None = None):
    from app.discovery.laboratory import run_lab_experiment
    result = await run_lab_experiment(lab_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Laboratory not found")
    return result


# ── Research Agents ──
@router.get("/agents")
async def api_list_research_agents(specialization: str | None = None):
    return await db.list_research_agents(specialization=specialization)


# ── Reports ──
@router.get("/reports")
async def api_list_reports(limit: int = 50):
    return await db.list_reports(limit=limit)


@router.get("/reports/{report_id}")
async def api_get_report(report_id: str):
    report = await db.get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.post("/reports/generate")
async def api_generate_report(data: dict):
    report = await generate_report(
        experiment_id=data.get("experiment_id"),
        pattern_id=data.get("pattern_id"),
        hypothesis_id=data.get("hypothesis_id"),
        agent_id=data.get("agent_id"),
    )
    return report


# ── Archive ──
@router.get("/archive")
async def api_list_archive(archive_type: str | None = None, limit: int = 100):
    return await db.list_archive(archive_type=archive_type, limit=limit)


@router.post("/archive/{experiment_id}")
async def api_archive_experiment(experiment_id: str):
    from app.discovery.archive import archive_experiment
    result = await archive_experiment(experiment_id)
    if not result:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return result


# ── Snapshots ──
@router.get("/snapshots")
async def api_get_snapshots(
    snapshot_type: str | None = None,
    metric_name: str | None = None,
    limit: int = 200,
):
    return await db.get_snapshots(snapshot_type=snapshot_type, metric_name=metric_name, limit=limit)


# ── State ──
@router.get("/state")
async def api_discovery_state():
    return await discovery_engine.get_full_state()


# ── Stats ──
@router.get("/stats")
async def api_discovery_stats():
    return await db.get_discovery_stats()
