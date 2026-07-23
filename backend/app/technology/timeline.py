import logging
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.timeline")


async def get_era(civ_id: str) -> str:
    level = await db.get_tech_level(civ_id)
    if not level:
        return "pre_industrial"
    avg = sum([
        level["computational_capability"],
        level["energy_capability"],
        level["manufacturing_capability"],
        level["scientific_knowledge"],
        level["automation_level"],
        level["infrastructure_level"],
    ]) / 6.0

    if avg >= 80:
        return "post_singularity"
    elif avg >= 60:
        return "digital_age"
    elif avg >= 40:
        return "industrial_age"
    elif avg >= 20:
        return "early_industrial"
    else:
        return "pre_industrial"


async def get_timeline(civ_id: str, limit: int = 50) -> list[dict]:
    return await db.list_timeline(civ_id, limit=limit)


def get_state() -> dict:
    return {"eras": ["pre_industrial", "early_industrial", "industrial_age", "digital_age", "post_singularity"], "initialized": True}
