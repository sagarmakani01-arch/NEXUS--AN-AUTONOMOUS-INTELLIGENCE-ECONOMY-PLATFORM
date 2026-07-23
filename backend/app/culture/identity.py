import logging
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.identity")

DEFAULT_CIV_NAMES = {
    "aetheria": "Aetheria", "synthara": "Synthara", "quantos": "Quantos",
    "nexaris": "Nexaris", "cybrix": "Cybrix",
}


async def initialize_identity(civ_id: str, name: str | None = None) -> dict:
    existing = await db.get_cultural_identity(civ_id)
    if existing:
        return existing

    civ_name = name or DEFAULT_CIV_NAMES.get(civ_id, f"Civilization {civ_id[:8]}")
    await db.create_cultural_identity(
        civilization_id=civ_id,
        name=civ_name,
        core_values='{"curiosity": 0.5, "solidarity": 0.5}',
        shared_history='[]',
        social_norms='[]',
        historical_symbols='[]',
        long_term_goals='[]',
        identity_strength=50.0,
    )
    await db.create_cultural_timeline(
        civilization_id=civ_id,
        change_type="civilization_founded",
        description=f"{civ_name} was founded",
        cause="genesis",
        impact_score=100.0,
    )
    return await db.get_cultural_identity(civ_id)


async def add_to_history(civ_id: str, event: str, impact: float = 50.0) -> None:
    identity = await db.get_cultural_identity(civ_id)
    if not identity:
        return
    history = list(identity.get("shared_history", []))
    history.append({"event": event, "impact": impact})
    if len(history) > 200:
        history = history[-200:]
    await db.update_cultural_identity(civ_id, shared_history=str(history).replace("'", '"'))


async def add_symbol(civ_id: str, symbol: str) -> None:
    identity = await db.get_cultural_identity(civ_id)
    if not identity:
        return
    symbols = list(identity.get("historical_symbols", []))
    if symbol not in symbols:
        symbols.append(symbol)
        await db.update_cultural_identity(civ_id, historical_symbols=str(symbols).replace("'", '"'))


async def add_goal(civ_id: str, goal: str) -> None:
    identity = await db.get_cultural_identity(civ_id)
    if not identity:
        return
    goals = list(identity.get("long_term_goals", []))
    if goal not in goals:
        goals.append(goal)
        await db.update_cultural_identity(civ_id, long_term_goals=str(goals).replace("'", '"'))


async def add_norm(civ_id: str, norm: str) -> None:
    identity = await db.get_cultural_identity(civ_id)
    if not identity:
        return
    norms = list(identity.get("social_norms", []))
    if norm not in norms:
        norms.append(norm)
        await db.update_cultural_identity(civ_id, social_norms=str(norms).replace("'", '"'))


def get_state() -> dict:
    return {"initialized": True}
