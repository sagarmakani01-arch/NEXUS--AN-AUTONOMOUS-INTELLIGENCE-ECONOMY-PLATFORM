import logging
import random

logger = logging.getLogger("nexus.planetary.settlements")


async def found_settlement(planet_id: str, region_id: str, civilization_id: str,
                           name: str) -> dict:
    from app.planetary import persistence as db
    sid = await db.create_settlement(
        planet_id=planet_id, region_id=region_id,
        civilization_id=civilization_id, name=name,
        population=random.randint(50, 200),
        economic_output=random.uniform(20.0, 60.0),
        infrastructure_level=random.uniform(5.0, 15.0),
        research_capacity=random.uniform(2.0, 10.0),
        quality_of_life=random.uniform(40.0, 60.0),
        education_level=random.uniform(5.0, 15.0),
    )
    await db.create_env_event(
        planet_id=planet_id, event_type="settlement_founded",
        region_id=region_id, title=f"Settlement '{name}' founded",
        severity=0.0, status="resolved",
    )
    return {"id": sid, "name": name}


async def grow_settlements(planet_id: str) -> dict:
    from app.planetary import persistence as db
    settlements = await db.list_settlements(planet_id)
    grew = 0
    for s in settlements:
        pop_growth = random.uniform(0.01, 0.05) * s["population"]
        new_pop = int(s["population"] + pop_growth)
        new_econ = min(100.0, s["economic_output"] + random.uniform(0.1, 0.5))
        new_qol = min(100.0, s["quality_of_life"] + random.uniform(-0.2, 0.3))
        new_edu = min(100.0, s["education_level"] + random.uniform(0.0, 0.2))
        new_research = min(100.0, s["research_capacity"] + random.uniform(0.0, 0.15))
        new_infra = min(100.0, s["infrastructure_level"] + random.uniform(0.0, 0.1))
        status = "growing" if new_pop > s["population"] else "stable" if new_pop == s["population"] else "declining"
        await db.update_settlement(s["id"],
            population=new_pop, economic_output=round(new_econ, 1),
            quality_of_life=round(new_qol, 1), education_level=round(new_edu, 1),
            research_capacity=round(new_research, 1),
            infrastructure_level=round(new_infra, 1), status=status)
        grew += 1
    return {"settlements_grew": grew}


def get_state() -> dict:
    return {"initialized": True}
