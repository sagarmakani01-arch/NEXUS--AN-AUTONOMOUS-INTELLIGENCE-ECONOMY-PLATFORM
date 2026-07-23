import logging
import random
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.dynamics")


async def initialize_dynamics(civ_id: str) -> dict:
    existing = await db.get_social_dynamics(civ_id)
    if existing:
        return existing
    await db.create_social_dynamics(
        civilization_id=civ_id,
        collaboration_score=50.0,
        competition_score=50.0,
        trust_level=50.0,
        influence_distribution="{}",
        knowledge_sharing_score=50.0,
        community_growth_rate=0.0,
    )
    return await db.get_social_dynamics(civ_id)


async def record_interaction(civ_id: str, interaction_type: str) -> dict | None:
    dynamics = await db.get_social_dynamics(civ_id)
    if not dynamics:
        return None
    updates = {}
    if interaction_type == "collaboration":
        delta = random.uniform(0.5, 2.0)
        updates["collaboration_score"] = min(100.0, dynamics["collaboration_score"] + delta)
        updates["trust_level"] = min(100.0, dynamics["trust_level"] + delta * 0.3)
    elif interaction_type == "competition":
        delta = random.uniform(0.5, 1.5)
        updates["competition_score"] = min(100.0, dynamics["competition_score"] + delta)
    elif interaction_type == "knowledge_share":
        delta = random.uniform(1.0, 3.0)
        updates["knowledge_sharing_score"] = min(100.0, dynamics["knowledge_sharing_score"] + delta)
    elif interaction_type == "conflict":
        delta = random.uniform(1.0, 3.0)
        updates["trust_level"] = max(0.0, dynamics["trust_level"] - delta)
        updates["collaboration_score"] = max(0.0, dynamics["collaboration_score"] - delta * 0.5)

    if updates:
        await db.update_social_dynamics(civ_id, **updates)
    return await db.get_social_dynamics(civ_id)


async def tick_dynamics(civ_id: str) -> dict | None:
    dynamics = await db.get_social_dynamics(civ_id)
    if not dynamics:
        return None
    drift = random.uniform(-0.5, 0.5)
    updates = {}
    for key in ["collaboration_score", "competition_score", "trust_level", "knowledge_sharing_score"]:
        current = dynamics.get(key, 50.0)
        new_val = max(0.0, min(100.0, current + drift * 0.1))
        updates[key] = round(new_val, 2)

    if updates:
        await db.update_social_dynamics(civ_id, **updates)
    return await db.get_social_dynamics(civ_id)


def get_state() -> dict:
    return {"initialized": True}
