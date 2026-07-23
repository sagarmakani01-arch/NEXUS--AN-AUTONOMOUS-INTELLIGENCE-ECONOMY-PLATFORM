import logging
import random
from app.culture import persistence as db
from app.culture import values as values_engine
from app.culture import identity as identity_engine
from app.culture import dynamics as dynamics_engine
from app.culture import memory as memory_engine

logger = logging.getLogger("nexus.culture.evolution")

CHANGE_TYPES = [
    "value_shift", "norm_emergence", "tradition_adaptation",
    "institutional_reform", "cultural_merger", "identity_crisis",
    "renaissance", "conservative_shift", "progressive_shift",
]


async def evolve_values(civ_id: str) -> dict:
    values = await db.get_value_system(civ_id)
    if not values:
        return {}
    top_value = max(values_engine.VALUE_NAMES, key=lambda v: values.get(v, 50.0))
    bottom_value = min(values_engine.VALUE_NAMES, key=lambda v: values.get(v, 50.0))
    top_val = values.get(top_value, 50.0)
    bottom_val = values.get(bottom_value, 50.0)
    if top_val - bottom_val > 40.0:
        transfer = random.uniform(0.5, 2.0)
        await values_engine.shift_value(civ_id, top_value, -transfer)
        await values_engine.shift_value(civ_id, bottom_value, transfer)
    if random.random() > 0.7:
        random_val = random.choice(values_engine.VALUE_NAMES)
        delta = random.uniform(-2.0, 2.0)
        await values_engine.shift_value(civ_id, random_val, delta)
    return await db.get_value_system(civ_id)


async def evolve_institutions(civ_id: str) -> dict:
    institutions = await db.list_institutions(civ_id)
    strengthened = 0
    weakened = 0
    for inst in institutions:
        if inst["strength"] < 30.0 and random.random() > 0.5:
            await db.update_institution(inst["id"], strength=inst["strength"] + 2.0)
            strengthened += 1
        elif inst["strength"] > 80.0 and random.random() > 0.8:
            new_influence = min(100.0, inst["influence"] + 3.0)
            await db.update_institution(inst["id"], influence=new_influence)
    return {"strengthened": strengthened, "weakened": weakened}


async def evolve_social_norms(civ_id: str) -> dict:
    dynamics = await db.get_social_dynamics(civ_id)
    if not dynamics:
        return {}
    identity = await db.get_cultural_identity(civ_id)
    if not identity:
        return {}
    new_norm = None
    if dynamics["collaboration_score"] > 70.0:
        new_norm = "collaborative_decision_making"
    elif dynamics["competition_score"] > 70.0:
        new_norm = "meritocratic_advancement"
    elif dynamics["knowledge_sharing_score"] > 70.0:
        new_norm = "open_knowledge_policy"
    elif dynamics["trust_level"] > 80.0:
        new_norm = "high_trust_society"

    if new_norm:
        norms = list(identity.get("social_norms", []))
        if new_norm not in norms:
            norms.append(new_norm)
            from sqlalchemy import select
            from app.core.database import async_session_factory
            from app.domain.models.culture import CulturalIdentity
            async with async_session_factory() as session:
                r = await session.execute(select(CulturalIdentity).where(CulturalIdentity.civilization_id == civ_id))
                o = r.scalar_one_or_none()
                if o:
                    import json
                    o.social_norms = json.dumps(norms)
                    o.identity_strength = min(100.0, o.identity_strength + 1.0)
                    await session.commit()
            await memory_engine.record_memory(civ_id, "norm_emergence",
                                               f"New norm emerged: {new_norm}",
                                               impact=25.0)
            return {"new_norm": new_norm}
    return {}


async def calculate_identity_score(civ_id: str) -> dict:
    values = await db.get_value_system(civ_id)
    dynamics = await db.get_social_dynamics(civ_id)
    institutions = await db.list_institutions(civ_id)
    communities = await db.list_communities(civ_id)

    knowledge_orient = (values.get("education", 50) + values.get("exploration", 50)) / 2 if values else 50.0
    innovation_orient = (values.get("innovation", 50) + values.get("exploration", 50)) / 2 if values else 50.0
    econ_stability = values.get("efficiency", 50) if values else 50.0
    social_cohesion = dynamics.get("collaboration_score", 50) if dynamics else 50.0
    inst_strength = (sum(i["strength"] for i in institutions) / max(1, len(institutions))) if institutions else 50.0
    adapt = (dynamics.get("knowledge_sharing_score", 50) + values.get("innovation", 50)) / 2 if (dynamics and values) else 50.0

    scores = {
        "civilization_id": civ_id,
        "knowledge_orientation": round(knowledge_orient, 1),
        "innovation_orientation": round(innovation_orient, 1),
        "economic_stability": round(econ_stability, 1),
        "social_cohesion": round(social_cohesion, 1),
        "institutional_strength": round(inst_strength, 1),
        "adaptability": round(adapt, 1),
    }

    existing = await db.get_identity_score(civ_id)
    if existing:
        await db.update_identity_score(civ_id, **{k: v for k, v in scores.items() if k != "civilization_id"})
    else:
        await db.create_identity_score(**scores)
    return scores


def get_state() -> dict:
    return {"change_types": CHANGE_TYPES, "initialized": True}
