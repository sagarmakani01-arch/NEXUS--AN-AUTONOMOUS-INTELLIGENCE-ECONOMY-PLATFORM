from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.meta.engine import meta_engine
from app.meta.observatory import observatory
from app.meta.analysis import analyzer
from app.meta.patterns import pattern_engine
from app.meta.evaluation import evaluator
from app.meta.experiments import experiment_manager
from app.meta.recommendations import recommender
from app.meta.knowledge import knowledge_base
from app.meta.explainability import explainer

router = APIRouter(prefix="/api/v1/meta", tags=["Meta Intelligence"])


class CompareRequest(BaseModel):
    simulation_a: str
    simulation_b: str


class ExperimentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    experiment_type: str = "controlled"
    control_id: Optional[str] = None
    variable_name: Optional[str] = None
    variable_change: Optional[dict] = None
    duration_ticks: int = 100


class KnowledgeRequest(BaseModel):
    title: str
    content: str
    entry_type: str = "insight"
    source: Optional[str] = None
    tags: Optional[list[str]] = None
    confidence: float = 0.5


# --- Engine State ---

@router.get("/state")
async def get_meta_state():
    return await meta_engine.get_full_state()


# --- Observatory ---

@router.get("/observatory/latest")
async def get_latest_observation(simulation_id: Optional[str] = "nexus_main"):
    obs = await observatory.get_latest_observation(simulation_id)
    if not obs:
        raise HTTPException(status_code=404, detail="No observations found")
    return obs


@router.get("/observatory/trends")
async def get_trends(
    simulation_id: str = "nexus_main",
    metric: str = Query("population", enum=["population", "economy", "research", "technology", "education", "governance", "environment", "innovation", "stability", "resources"]),
    span: int = Query(50, ge=5, le=500),
):
    return await observatory.get_trend(simulation_id, metric, span)


# --- Cross-Simulation Analysis ---

@router.post("/analysis/compare")
async def compare_simulations(request: CompareRequest):
    results = await meta_engine.compare_simulations(request.simulation_a, request.simulation_b)
    return {"comparison": results}


@router.get("/analysis/results")
async def get_analysis_results():
    return {"results": await analyzer.get_results()}


# --- Pattern Discovery ---

@router.post("/patterns/discover")
async def discover_patterns():
    return {"patterns": await meta_engine.discover_patterns()}


@router.get("/patterns")
async def get_patterns(pattern_type: Optional[str] = None):
    return {"patterns": await pattern_engine.get_patterns(pattern_type)}


@router.get("/patterns/high-confidence")
async def get_high_confidence_patterns(min_confidence: float = Query(0.7, ge=0.0, le=1.0)):
    return {"patterns": await pattern_engine.get_patterns_by_confidence(min_confidence)}


# --- Rule Evaluation ---

@router.post("/rules/evaluate")
async def evaluate_rules(rule_name: Optional[str] = Query(None)):
    return {"evaluations": await meta_engine.evaluate_rules(rule_name)}


@router.get("/rules/evaluations")
async def get_rule_evaluations(domain: Optional[str] = None):
    return {"evaluations": await evaluator.get_evaluations(domain)}


@router.get("/rules/report")
async def generate_rule_report(domain: Optional[str] = None):
    report = await evaluator.generate_report(domain)
    return {"report": report}


# --- Experiments ---

@router.post("/experiments/create")
async def create_experiment(request: ExperimentCreateRequest):
    return await experiment_manager.create_experiment(
        name=request.name,
        description=request.description or "",
        experiment_type=request.experiment_type,
        control_id=request.control_id,
        variable_name=request.variable_name,
        variable_change=request.variable_change,
        duration_ticks=request.duration_ticks,
    )


@router.post("/experiments/{exp_id}/run")
async def run_experiment(exp_id: str):
    return await experiment_manager.run_experiment(exp_id)


@router.get("/experiments")
async def get_experiments(status: Optional[str] = None):
    return {"experiments": await experiment_manager.get_experiments(status)}


@router.get("/experiments/{exp_id}/compare")
async def compare_experiment(exp_id: str):
    return await experiment_manager.compare_experiment(exp_id)


# --- Recommendations ---

@router.post("/recommendations/generate")
async def generate_recommendations(domain: Optional[str] = Query(None)):
    return {"recommendations": await meta_engine.generate_recommendations(domain)}


@router.get("/recommendations")
async def get_recommendations(status: Optional[str] = Query(None, enum=["pending", "accepted", "rejected"])):
    return {"recommendations": await recommender.get_recommendations(status)}


@router.post("/recommendations/{rec_id}/review")
async def review_recommendation(rec_id: str, status: str = Query(..., enum=["accepted", "rejected"])):
    return await recommender.review_recommendation(rec_id, status)


# --- Knowledge Base ---

@router.post("/knowledge/add")
async def add_knowledge(request: KnowledgeRequest):
    return await knowledge_base.add_entry(
        title=request.title,
        content=request.content,
        entry_type=request.entry_type,
        source=request.source,
        tags=request.tags,
        confidence=request.confidence,
    )


@router.get("/knowledge")
async def get_knowledge(entry_type: Optional[str] = None):
    return {"entries": await knowledge_base.get_entries(entry_type)}


@router.post("/knowledge/insight")
async def record_insight(insight: str = Query(...), source: Optional[str] = None):
    return await knowledge_base.record_insight(insight, source)


# --- Reports ---

@router.post("/reports/generate")
async def generate_report(
    title: str = Query(...),
    report_type: str = Query("analysis", enum=["analysis", "summary", "comparison", "insight"]),
    content: Optional[str] = None,
):
    return await knowledge_base.generate_report(
        title=title,
        report_type=report_type,
        content=content,
    )


@router.get("/reports")
async def get_reports(report_type: Optional[str] = None):
    return {"reports": await knowledge_base.get_reports(report_type)}


# --- Explainability ---

@router.get("/explain/recommendation/{rec_id}")
async def explain_recommendation(rec_id: str):
    return await explainer.explain_recommendation(rec_id)


@router.get("/explain/pattern/{pattern_id}")
async def explain_pattern(pattern_id: str):
    return await explainer.explain_pattern(pattern_id)


@router.get("/explain/experiment/{exp_id}")
async def explain_experiment(exp_id: str):
    return await explainer.explain_experiment_result(exp_id)
