import json
import logging
import random
import uuid

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.auto_experiment")


OBSERVATION_TEMPLATES = [
    "Civilizations with stronger {variable} exhibit higher {outcome}",
    "Increased {variable} correlates with decreased {outcome}",
    "{variable} shows cyclic patterns over long time scales",
    "High {variable} environments lead to accelerated {outcome}",
    "Communities that invest in {variable} have more stable {outcome}",
]

VARIABLE_POOL = [
    "education", "technology", "trade", "communication", "governance",
    "healthcare", "infrastructure", "cultural_exchange", "knowledge_sharing",
    "environmental_awareness", "military_spending", "research_funding",
    "social_mobility", "resource_management", "population_density",
]

OUTCOME_POOL = [
    "economic_growth", "innovation_rate", "social_stability", "population_health",
    "environmental_quality", "cultural_diversity", "technological_progress",
    "quality_of_life", "conflict_resolution", "knowledge_accumulation",
]


async def generate_experiment() -> dict:
    variable = random.choice(VARIABLE_POOL)
    outcome = random.choice(OUTCOME_POOL)
    template = random.choice(OBSERVATION_TEMPLATES)
    observation = template.format(variable=variable, outcome=outcome)

    experiment_type = random.choice(["correlation", "causation", "dose_response", "longitudinal"])
    var_change = random.choice(["increase", "decrease", "double", "halve", "set_to_zero"])

    experiment = await db.create_auto_experiment(
        trigger_observation=observation,
        experiment_type=experiment_type,
        variable_name=variable,
        variable_change=var_change,
        duration_ticks=random.randint(20, 100),
        status="pending",
    )

    result = await _run_auto_experiment_simulation(experiment)

    await db.create_auto_experiment(
        id=experiment["id"],
        trigger_observation=observation,
        experiment_type=experiment_type,
        variable_name=variable,
        variable_change=var_change,
        duration_ticks=experiment["duration_ticks"],
        status="completed",
        result_summary=json.dumps(result),
        significance=result.get("significance", 0.0),
    )

    return await db.get_experiment(experiment["id"])


async def _run_auto_experiment_simulation(experiment: dict) -> dict:
    duration = experiment.get("duration_ticks", 50)
    variable = experiment.get("variable_name", "unknown")
    change = experiment.get("variable_change", "increase")

    baseline = []
    for _t in range(duration):
        baseline.append(random.gauss(0.5, 0.1))

    modified = []
    effect_mult = {"increase": 1.3, "decrease": 0.7, "double": 2.0, "halve": 0.5, "set_to_zero": 0.0}
    mult = effect_mult.get(change, 1.0)
    for _t in range(duration):
        modified.append(random.gauss(0.5 * mult, 0.1))

    baseline_mean = sum(baseline) / len(baseline) if baseline else 0
    modified_mean = sum(modified) / len(modified) if modified else 0
    diff = modified_mean - baseline_mean
    noise_level = 0.1
    significance = min(1.0, abs(diff) / (noise_level + 0.001))

    return {
        "variable": variable,
        "change_applied": change,
        "baseline_mean": round(baseline_mean, 4),
        "modified_mean": round(modified_mean, 4),
        "difference": round(diff, 4),
        "significance": round(significance, 4),
        "sample_size": duration,
        "observation": experiment.get("trigger_observation", ""),
    }
