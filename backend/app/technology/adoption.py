import logging
import random
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.adoption")


async def evaluate_adoption(civ_id: str, tech_id: str) -> dict:
    tech = await db.get_technology(tech_id)
    if not tech:
        return {"decision": "unknown_technology"}

    tech_level = await db.get_tech_level(civ_id)
    base_benefit = tech["impact_score"] * random.uniform(0.3, 1.0)
    base_cost = tech["difficulty_level"] * random.uniform(0.2, 0.8)
    risk = tech["difficulty_level"] * random.uniform(0.1, 0.5)

    infra = tech_level["infrastructure_level"] if tech_level else 10.0
    if infra < tech["difficulty_level"] * 0.5:
        risk *= 2.0
        base_benefit *= 0.5

    cultural_compat = random.uniform(40.0, 90.0)
    strategic = random.uniform(30.0, 80.0)
    score = base_benefit - base_cost - risk * 0.5 + cultural_compat * 0.1 + strategic * 0.1

    decision = "adopt" if score > 10 else "defer" if score > -10 else "reject"
    await db.create_adoption(
        civilization_id=civ_id,
        technology_id=tech_id,
        decision=decision,
        economic_benefit=round(base_benefit, 2),
        cost=round(base_cost, 2),
        risk=round(risk, 2),
        cultural_compatibility=round(cultural_compat, 2),
        strategic_importance=round(strategic, 2),
    )

    if decision == "adopt":
        await db.create_timeline_event(
            civilization_id=civ_id,
            event_type="technology_adopted",
            technology_id=tech_id,
            title=f"Adopted {tech['name']}",
            impact_score=base_benefit,
        )
        await db.update_technology(tech_id, adoption_count=(tech.get("adoption_count", 0) or 0) + 1)

    return {"decision": decision, "economic_benefit": base_benefit, "cost": base_cost, "risk": risk}


def get_state() -> dict:
    return {"factors": ["economic_benefit", "cost", "risk", "cultural_compatibility", "strategic_importance"], "initialized": True}
