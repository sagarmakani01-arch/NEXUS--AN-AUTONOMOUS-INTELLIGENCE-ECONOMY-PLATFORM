import logging
import random
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.obsolescence")

OBsolescence_FACTORS = ["better_alternatives", "resource_cost", "efficiency_improvement", "market_change"]


async def check_obsolescence(civ_id: str) -> list[dict]:
    techs = await db.list_technologies(status="mature")
    obsolete = []
    for tech in techs:
        decay = random.uniform(0.0, 2.0)
        if tech["maturity"] > 80.0 and decay > 1.5:
            await db.update_technology(tech["id"], status="obsolete", maturity=0.0)
            await db.create_timeline_event(
                civilization_id=civ_id,
                event_type="technology_obsolete",
                technology_id=tech["id"],
                title=f"{tech['name']} became obsolete",
                impact_score=5.0,
            )
            obsolete.append({"id": tech["id"], "name": tech["name"]})
    return obsolete


def get_state() -> dict:
    return {"factors": OBsolescence_FACTORS, "initialized": True}
