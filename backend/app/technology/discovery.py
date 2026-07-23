import logging
import random
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.discovery")


async def attempt_discovery(civ_id: str, method: str = "research") -> dict | None:
    techs = await db.list_technologies(status="concept")
    if not techs:
        return None
    candidates = [t for t in techs if t["origin_civilization_id"] != civ_id] or techs
    tech = random.choice(candidates)
    success_chance = 0.3 + (0.2 if method == "collaboration" else 0) + (0.1 if method == "experimentation" else 0)
    if random.random() > success_chance:
        return None

    disc_id = await db.create_discovery(
        civilization_id=civ_id,
        technology_id=tech["id"],
        title=f"Discovery: {tech['name']}",
        description=f"New discovery in {tech['domain']} via {method}",
        difficulty=random.choice(["easy", "medium", "hard"]),
        impact_score=tech["impact_score"] * random.uniform(0.5, 1.0),
        method=method,
        confidence=random.uniform(40.0, 90.0),
    )
    await db.create_timeline_event(
        civilization_id=civ_id,
        event_type="discovery_made",
        technology_id=tech["id"],
        title=f"Discovered {tech['name']}",
        impact_score=tech["impact_score"],
    )
    logger.info("Discovery made: %s by civ %s", tech["name"], civ_id)
    return await db.list_discoveries(civ_id)


def get_state() -> dict:
    return {"methods": ["research", "collaboration", "experimentation", "cross_domain"], "initialized": True}
