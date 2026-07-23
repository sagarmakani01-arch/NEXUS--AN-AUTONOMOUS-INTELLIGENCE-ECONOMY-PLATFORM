import logging
import random

logger = logging.getLogger("nexus.planetary.sustainability")


async def calculate_sustainability(planet_id: str, civilization_id: str) -> dict:
    from app.planetary import persistence as db
    settlements = await db.list_settlements(planet_id, civilization_id=civilization_id)
    resources = await db.list_resources(planet_id)
    infra_list = await db.list_infrastructure(planet_id, civilization_id=civilization_id)

    total_pop = sum(s["population"] for s in settlements)
    total_econ = sum(s["economic_output"] for s in settlements)
    avg_infra_eff = (sum(i["efficiency"] for i in infra_list) / max(1, len(infra_list))) if infra_list else 50.0

    consumed = total_pop * 0.1 + total_econ * 0.05
    renewable = sum(r["quantity"] for r in resources if r["renewable"])
    total_res = sum(r["quantity"] for r in resources)
    renewable_pct = (renewable / max(1, total_res)) * 100

    health = 80.0 - consumed * 0.1 + renewable_pct * 0.2
    health = max(10.0, min(100.0, health))
    carbon = total_econ * 0.3 + total_pop * 0.02
    restoration = random.uniform(0.0, 5.0)
    score = (health * 0.3 + renewable_pct * 0.2 + avg_infra_eff * 0.2 + (100 - carbon) * 0.1 + restoration * 0.2)
    score = max(0.0, min(100.0, score))

    await db.create_sustainability(
        planet_id=planet_id, civilization_id=civilization_id,
        resource_consumption_rate=round(consumed, 2),
        renewable_usage_pct=round(renewable_pct, 1),
        infrastructure_efficiency=round(avg_infra_eff, 1),
        environmental_health=round(health, 1),
        carbon_footprint=round(carbon, 2),
        restoration_effort=round(restoration, 2),
        sustainability_score=round(score, 1),
    )
    return {"sustainability_score": round(score, 1), "environmental_health": round(health, 1)}


def get_state() -> dict:
    return {"initialized": True}
