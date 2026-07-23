import json
import logging
import random

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.validation")


async def validate_hypothesis(hypothesis_id: str) -> dict | None:
    hypothesis = await db.get_hypothesis(hypothesis_id)
    if not hypothesis:
        return None

    experiments = await db.list_experiments(limit=20)
    relevant_experiments = _find_relevant_experiments(hypothesis, experiments)

    validation_result = await _run_validation_simulation(hypothesis, relevant_experiments)

    validation = await db.create_validation(
        hypothesis_id=hypothesis_id,
        experiment_id=validation_result.get("experiment_id"),
        validation_type="simulation",
        outcome=validation_result.get("outcome", "inconclusive"),
        confidence_delta=validation_result.get("confidence_delta", 0.0),
        notes=json.dumps(validation_result.get("details", {})),
    )

    current_confidence = hypothesis.get("confidence_level", 0.0)
    new_confidence = max(0.0, min(1.0, current_confidence + validation_result.get("confidence_delta", 0.0)))

    await db.update_hypothesis(hypothesis_id, confidence_level=new_confidence)

    return await db.get_hypothesis(hypothesis_id)


def _find_relevant_experiments(hypothesis: dict, experiments: list[dict]) -> list[dict]:
    hyp_text = f"{hypothesis.get('title', '')} {hypothesis.get('description', '')}".lower()
    relevant = []
    for exp in experiments:
        exp_text = f"{exp.get('title', '')} {exp.get('research_question', '')}".lower()
        common = set(hyp_text.split()) & set(exp_text.split())
        if len(common) > 3:
            relevant.append(exp)
    return relevant[:5]


async def _run_validation_simulation(hypothesis: dict, experiments: list[dict]) -> dict:
    confidence = hypothesis.get("confidence_level", 0.5)
    noise = random.gauss(0, 0.1)
    outcome_roll = random.random()

    if outcome_roll < 0.4:
        outcome = "confirmed"
        delta = random.uniform(0.05, 0.2)
    elif outcome_roll < 0.7:
        outcome = "inconclusive"
        delta = random.uniform(-0.05, 0.05)
    else:
        outcome = "refuted"
        delta = random.uniform(-0.2, -0.05)

    return {
        "outcome": outcome,
        "confidence_delta": round(delta, 4),
        "experiment_id": experiments[0]["id"] if experiments else None,
        "details": {
            "initial_confidence": confidence,
            "new_confidence": max(0.0, min(1.0, confidence + delta)),
            "experiments_used": len(experiments),
            "noise_level": round(noise, 4),
        },
    }
