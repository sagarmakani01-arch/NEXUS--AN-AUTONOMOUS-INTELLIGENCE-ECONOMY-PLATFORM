import logging
import random
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.competition")

COMPETITION_TYPES = ["research_speed", "patent_quality", "innovation_count", "manufacturing"]


async def run_competition(civ_a_id: str, civ_b_id: str, comp_type: str | None = None) -> dict:
    if comp_type not in COMPETITION_TYPES:
        comp_type = random.choice(COMPETITION_TYPES)

    tech_a = await db.get_tech_level(civ_a_id)
    tech_b = await db.get_tech_level(civ_b_id)

    score_a = sum([
        (tech_a.get("computational_capability", 10) if tech_a else 10) * 0.3,
        (tech_a.get("scientific_knowledge", 10) if tech_a else 10) * 0.4,
        (tech_a.get("manufacturing_capability", 10) if tech_a else 10) * 0.3,
    ])
    score_b = sum([
        (tech_b.get("computational_capability", 10) if tech_b else 10) * 0.3,
        (tech_b.get("scientific_knowledge", 10) if tech_b else 10) * 0.4,
        (tech_b.get("manufacturing_capability", 10) if tech_b else 10) * 0.3,
    ])

    score_a += random.uniform(-5.0, 5.0)
    score_b += random.uniform(-5.0, 5.0)

    winner = civ_a_id if score_a > score_b else civ_b_id
    return {"competition_type": comp_type, "winner": winner, "score_a": round(score_a, 1), "score_b": round(score_b, 1)}


def get_state() -> dict:
    return {"competition_types": COMPETITION_TYPES, "initialized": True}
