import json
import logging
import random
import uuid

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.experiment")


DEFAULT_VARIABLE_TEMPLATES = {
    "economy": {
        "education_investment": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.3},
        "tax_rate": {"type": "float", "min": 0.0, "max": 0.5, "default": 0.1},
        "trade_openness": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.5},
    },
    "social": {
        "community_size": {"type": "int", "min": 10, "max": 1000, "default": 100},
        "communication_frequency": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.3},
        "trust_initial": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.5},
    },
    "technology": {
        "innovation_rate": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.1},
        "knowledge_transfer_speed": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.3},
        "research_funding": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.2},
    },
    "environment": {
        "resource_abundance": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.5},
        "climate_stability": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.7},
        "population_density": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.3},
    },
    "governance": {
        "regulation_level": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.3},
        "decentralization": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.5},
        "participation_rate": {"type": "float", "min": 0.0, "max": 1.0, "default": 0.4},
    },
}


async def create_controlled_experiment(
    title: str,
    research_question: str | None = None,
    hypothesis: str | None = None,
    variables: dict | None = None,
    constraints: dict | None = None,
    simulation_params: dict | None = None,
    duration_ticks: int = 100,
    laboratory_type: str = "general",
    created_by: str | None = None,
    tags: list | None = None,
) -> dict:
    return await db.create_experiment(
        title=title,
        research_question=research_question or "",
        hypothesis=hypothesis or "",
        variables=json.dumps(variables or {}),
        constraints=json.dumps(constraints or {}),
        simulation_params=json.dumps(simulation_params or {}),
        duration_ticks=duration_ticks,
        status="draft",
        laboratory_type=laboratory_type,
        created_by=created_by or "system",
        tags=json.dumps(tags or []),
    )


async def run_experiment(experiment_id: str) -> dict | None:
    experiment = await db.get_experiment(experiment_id)
    if not experiment:
        return None

    await db.update_experiment(
        experiment_id,
        status="running",
        started_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    )

    result = await _simulate_experiment(experiment)
    await db.update_experiment(
        experiment_id,
        status="completed",
        result_summary=json.dumps(result),
        confidence_score=result.get("confidence", 0.0),
        completed_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
    )
    return await db.get_experiment(experiment_id)


async def _simulate_experiment(experiment: dict) -> dict:
    variables = experiment.get("variables", {})
    duration = experiment.get("duration_ticks", 100)

    control_results = {}
    for var_name, var_val in variables.items():
        base_values = []
        for _t in range(duration):
            noise = random.gauss(0, 0.05)
            val = _simulate_metric(var_val, noise)
            base_values.append(val)
        control_results[var_name] = {
            "mean": sum(base_values) / len(base_values) if base_values else 0,
            "std": _calculate_std(base_values),
            "final": base_values[-1] if base_values else 0,
            "trend": base_values[-1] - base_values[0] if len(base_values) > 1 else 0,
        }

    test_results = {}
    for var_name, var_val in variables.items():
        test_values = []
        modified = _modify_variable(var_val)
        for _t in range(duration):
            noise = random.gauss(0, 0.05)
            val = _simulate_metric(modified, noise)
            test_values.append(val)
        test_results[var_name] = {
            "mean": sum(test_values) / len(test_values) if test_values else 0,
            "std": _calculate_std(test_values),
            "final": test_values[-1] if test_values else 0,
            "trend": test_values[-1] - test_values[0] if len(test_values) > 1 else 0,
        }

    effect_sizes = {}
    for var_name in variables:
        control_mean = control_results[var_name]["mean"]
        test_mean = test_results[var_name]["mean"]
        pooled_std = ((control_results[var_name]["std"] ** 2 + test_results[var_name]["std"] ** 2) / 2) ** 0.5
        effect_size = (test_mean - control_mean) / (pooled_std + 0.001)
        effect_sizes[var_name] = round(effect_size, 4)

    overall_effect = abs(sum(effect_sizes.values())) / len(effect_sizes) if effect_sizes else 0
    confidence = min(1.0, overall_effect * 0.8 + 0.2)

    return {
        "control": control_results,
        "test": test_results,
        "effect_sizes": effect_sizes,
        "confidence": round(confidence, 4),
        "sample_size": duration,
        "significant": overall_effect > 0.1,
    }


def _simulate_metric(value: float | int, noise: float) -> float:
    base = float(value) if isinstance(value, (int, float)) else 0.5
    drift = random.uniform(-0.02, 0.02)
    return max(0, base + drift + noise)


def _modify_variable(value: float | int) -> float:
    v = float(value) if isinstance(value, (int, float)) else 0.5
    delta = random.uniform(0.1, 0.4)
    return min(1.0, max(0.0, v + delta if random.random() > 0.5 else v - delta))


def _calculate_std(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return variance ** 0.5


async def compare_experiments(experiment_ids: list[str]) -> dict:
    results = {}
    for eid in experiment_ids:
        exp = await db.get_experiment(eid)
        if exp:
            results[eid] = {
                "title": exp.get("title", ""),
                "status": exp.get("status", ""),
                "confidence_score": exp.get("confidence_score", 0),
                "result_summary": exp.get("result_summary"),
            }
    return {
        "experiments": results,
        "comparison_count": len(results),
    }
