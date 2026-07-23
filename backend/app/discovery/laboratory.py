import json
import logging
import random
import uuid

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.laboratory")


DEFAULT_LABS = [
    {
        "name": "Economic Laboratory",
        "lab_type": "economic",
        "description": "Studies economic systems, market dynamics, wealth distribution, and resource allocation",
        "specialization": json.dumps(["market_analysis", "wealth_distribution", "resource_allocation", "trade_dynamics"]),
    },
    {
        "name": "Social Laboratory",
        "lab_type": "social",
        "description": "Examines social structures, communication patterns, trust networks, and community dynamics",
        "specialization": json.dumps(["social_networks", "trust_dynamics", "communication_patterns", "community_formation"]),
    },
    {
        "name": "Evolution Laboratory",
        "lab_type": "evolution",
        "description": "Investigates evolutionary processes, adaptation mechanisms, and innovation emergence",
        "specialization": json.dumps(["evolutionary_dynamics", "innovation_emergence", "adaptation_mechanisms"]),
    },
    {
        "name": "Technology Laboratory",
        "lab_type": "technology",
        "description": "Explores technological progress, knowledge diffusion, and research impact",
        "specialization": json.dumps(["technology_adoption", "knowledge_diffusion", "research_impact", "innovation_rate"]),
    },
    {
        "name": "Environmental Laboratory",
        "lab_type": "environmental",
        "description": "Analyzes environmental systems, resource sustainability, and climate effects",
        "specialization": json.dumps(["resource_management", "climate_analysis", "sustainability", "population_dynamics"]),
    },
    {
        "name": "Governance Laboratory",
        "lab_type": "governance",
        "description": "Studies governance structures, policy impacts, and decision-making systems",
        "specialization": json.dumps(["policy_analysis", "governance_structures", "voting_systems", "regulation_impact"]),
    },
]


async def initialize_laboratories():
    existing = await db.list_laboratories()
    if existing:
        return existing
    created = []
    for lab_data in DEFAULT_LABS:
        lab = await db.create_laboratory(**lab_data)
        created.append(lab)
    logger.info("Initialized %d research laboratories", len(created))
    return created


async def run_lab_experiment(lab_id: str, experiment_config: dict | None = None) -> dict | None:
    lab = await db.get_laboratory(lab_id)
    if not lab:
        return None
    return await _conduct_lab_experiment(lab, experiment_config)


async def auto_run_labs() -> list[dict]:
    labs = await db.list_laboratories()
    results = []
    for lab in labs:
        if lab.get("active", True):
            result = await _conduct_lab_experiment(lab)
            results.append(result)
    return results


async def _conduct_lab_experiment(lab: dict, config: dict | None = None) -> dict:
    lab_type = lab.get("lab_type", "general")
    specializations = lab.get("specialization", [])

    var_pool = {
        "economic": {"tax_rate": 0.1, "education_investment": 0.3, "trade_openness": 0.5},
        "social": {"community_size": 100, "communication_frequency": 0.3, "trust_initial": 0.5},
        "evolution": {"mutation_rate": 0.01, "selection_pressure": 0.3, "generation_time": 10},
        "technology": {"innovation_rate": 0.1, "knowledge_transfer": 0.3, "research_funding": 0.2},
        "environmental": {"resource_abundance": 0.5, "climate_stability": 0.7, "population_growth": 0.3},
        "governance": {"regulation_level": 0.3, "decentralization": 0.5, "participation_rate": 0.4},
    }
    variables = var_pool.get(lab_type, var_pool["social"]).copy()
    if config:
        variables.update(config)

    import random as rnd
    control_mean = rnd.uniform(0.3, 0.7)
    effect = rnd.uniform(-0.2, 0.2)
    test_mean = max(0, min(1, control_mean + effect))

    significance = abs(effect) / (0.1 + 0.001)
    spec = random.choice(specializations) if specializations else lab_type

    experiment = await db.create_experiment(
        title=f"Auto experiment - {lab['name']}",
        research_question=f"What is the effect of variables on {spec}?",
        hypothesis=f"Modifying {spec} parameters will produce measurable changes",
        variables=json.dumps(variables),
        constraints=json.dumps({"lab_type": lab_type, "specialization": spec}),
        simulation_params=json.dumps({"duration": 50, "iterations": 1}),
        duration_ticks=50,
        status="completed",
        result_summary=json.dumps({
            "control_mean": round(control_mean, 4),
            "test_mean": round(test_mean, 4),
            "effect_size": round(effect, 4),
            "significance": round(min(1.0, significance), 4),
        }),
        confidence_score=round(min(1.0, significance * 0.3 + 0.2), 4),
        laboratory_type=lab_type,
        created_by="laboratory_auto",
        tags=json.dumps(["auto", lab_type, spec]),
    )

    await db.update_laboratory(lab["id"], experiment_count=lab.get("experiment_count", 0) + 1)

    return experiment
