import logging
import random
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.values")

VALUE_NAMES = [
    "innovation", "cooperation", "competition", "education",
    "efficiency", "sustainability", "exploration", "security", "transparency",
]


async def initialize_values(civ_id: str, **overrides) -> dict:
    existing = await db.get_value_system(civ_id)
    if existing:
        return existing
    defaults = {v: 50.0 for v in VALUE_NAMES}
    defaults.update(overrides)
    await db.create_value_system(civilization_id=civ_id, **defaults)
    return await db.get_value_system(civ_id)


async def shift_value(civ_id: str, value_name: str, delta: float) -> dict | None:
    if value_name not in VALUE_NAMES:
        return None
    values = await db.get_value_system(civ_id)
    if not values:
        return None
    current = values.get(value_name, 50.0)
    new_val = max(0.0, min(100.0, current + delta))
    await db.update_value_system(civ_id, **{value_name: new_val})
    if abs(delta) > 5.0:
        await db.create_cultural_timeline(
            civilization_id=civ_id,
            change_type="value_shift",
            description=f"{value_name} shifted by {delta:+.1f}",
            cause="cultural_evolution",
            impact_score=abs(delta),
        )
    return await db.get_value_system(civ_id)


async def apply_event_influence(civ_id: str, event_type: str) -> dict | None:
    shifts = {
        "discovery": {"innovation": 2.0, "exploration": 1.5, "education": 1.0},
        "crisis": {"cooperation": 2.0, "security": 2.5, "sustainability": 1.0},
        "trade_deal": {"cooperation": 1.0, "efficiency": 1.5, "transparency": 0.5},
        "conflict": {"security": 2.0, "competition": 1.5, "cooperation": -1.0},
        "innovation": {"innovation": 2.5, "education": 1.5, "exploration": 1.0},
        "education": {"education": 2.5, "innovation": 1.0, "transparency": 1.0},
        "migration": {"exploration": 1.5, "cooperation": 1.0, "sustainability": -0.5},
        "governance_change": {"transparency": 1.5, "security": 1.0, "cooperation": 0.5},
    }
    event_shifts = shifts.get(event_type, {})
    if not event_shifts:
        return None
    values = await db.get_value_system(civ_id)
    if not values:
        return None
    for val_name, delta in event_shifts.items():
        jitter = random.uniform(-0.5, 0.5)
        current = values.get(val_name, 50.0)
        new_val = max(0.0, min(100.0, current + delta + jitter))
        await db.update_value_system(civ_id, **{val_name: round(new_val, 2)})
    return await db.get_value_system(civ_id)


def get_decision_influence(values: dict) -> dict:
    influences = {}
    for v in VALUE_NAMES:
        score = values.get(v, 50.0)
        influences[v] = (score - 50.0) / 50.0
    return influences


def get_state() -> dict:
    return {"value_names": VALUE_NAMES, "initialized": True}
