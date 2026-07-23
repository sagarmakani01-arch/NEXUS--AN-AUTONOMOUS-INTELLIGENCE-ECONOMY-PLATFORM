import logging
import random

logger = logging.getLogger("nexus.planetary.infrastructure")

INFRA_TYPES = ["road", "rail", "port", "power", "communication", "research_facility", "water_supply"]


async def build_infrastructure(planet_id: str, region_id: str, civilization_id: str,
                                infra_type: str, name: str | None = None) -> dict:
    from app.planetary import persistence as db
    if infra_type not in INFRA_TYPES:
        infra_type = random.choice(INFRA_TYPES)
    iid = await db.create_infrastructure(
        planet_id=planet_id, region_id=region_id,
        civilization_id=civilization_id, infra_type=infra_type,
        name=name or f"{infra_type.replace('_', ' ').title()} in {region_id[:8]}",
        level=1, efficiency=50.0, condition=100.0,
        cost=random.uniform(100, 500),
    )
    return {"id": iid, "type": infra_type, "level": 1}


async def upgrade_infrastructure(infra_id: str) -> dict | None:
    from app.planetary import persistence as db
    infra_list = await db.list_infrastructure(planet_id="")
    infra = next((i for i in infra_list if i["id"] == infra_id), None)
    if not infra:
        return None
    new_level = min(10, infra["level"] + 1)
    new_eff = min(100.0, infra["efficiency"] + 5.0)
    await db.update_infrastructure(infra_id, level=new_level, efficiency=round(new_eff, 1))
    return {"new_level": new_level, "efficiency": new_eff}


async def tick_infrastructure(planet_id: str) -> dict:
    from app.planetary import persistence as db
    infra_list = await db.list_infrastructure(planet_id)
    degraded = 0
    for i in infra_list:
        decay = random.uniform(0.1, 0.5)
        new_cond = max(0.0, i["condition"] - decay)
        await db.update_infrastructure(i["id"], condition=round(new_cond, 1))
        if new_cond < 20.0:
            degraded += 1
    return {"degraded": degraded}


def get_state() -> dict:
    return {"infra_types": INFRA_TYPES, "initialized": True}
