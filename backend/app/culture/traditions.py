import logging
from datetime import datetime, timezone, timedelta
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.traditions")

TRADITION_TEMPLATES = [
    {"name": "Research Summit", "description": "Annual gathering of researchers", "frequency": "annual", "impact": 30.0},
    {"name": "Innovation Festival", "description": "Celebration of technological breakthroughs", "frequency": "annual", "impact": 25.0},
    {"name": "Knowledge Week", "description": "Week-long knowledge sharing event", "frequency": "annual", "impact": 20.0},
    {"name": "Founders Day", "description": "Commemoration of civilization founding", "frequency": "annual", "impact": 40.0},
    {"name": "Trade Fair", "description": "Marketplace and trade exhibition", "frequency": "biannual", "impact": 15.0},
    {"name": "Cultural Exchange", "description": "Inter-civilization cultural sharing", "frequency": "annual", "impact": 20.0},
    {"name": "Science Symposium", "description": "Academic research presentations", "frequency": "quarterly", "impact": 18.0},
    {"name": "Heritage Day", "description": "Celebration of cultural heritage", "frequency": "annual", "impact": 25.0},
]


async def initialize_traditions(civ_id: str) -> list[dict]:
    existing = await db.list_traditions(civ_id)
    if existing:
        return existing
    created = []
    for t in TRADITION_TEMPLATES[:4]:
        now = datetime.now(timezone.utc)
        tid = await db.create_tradition(
            civilization_id=civ_id,
            name=t["name"],
            description=t["description"],
            frequency=t["frequency"],
            impact_score=t["impact"],
            established_date=now,
            next_held=now + timedelta(days=365),
        )
        created.append({"id": tid, "name": t["name"]})
    logger.info("Initialized %d traditions for civ %s", len(created), civ_id)
    return created


async def create_tradition(civ_id: str, name: str, description: str | None = None,
                           frequency: str = "annual", impact: float = 20.0) -> dict:
    now = datetime.now(timezone.utc)
    tid = await db.create_tradition(
        civilization_id=civ_id,
        name=name,
        description=description,
        frequency=frequency,
        impact_score=impact,
        established_date=now,
        next_held=now + timedelta(days=365),
    )
    await db.create_cultural_timeline(
        civilization_id=civ_id,
        change_type="tradition_established",
        description=f"Tradition '{name}' established",
        cause="cultural_initiative",
        impact_score=impact,
    )
    traditions = await db.list_traditions(civ_id)
    return next((t for t in traditions if t["id"] == tid), {})


async def hold_tradition(trad_id: str) -> dict | None:
    traditions = await db.list_traditions()
    trad = next((t for t in traditions if t["id"] == trad_id), None)
    if not trad:
        return None
    now = datetime.now(timezone.utc)
    freq_map = {"daily": 1, "weekly": 7, "monthly": 30, "quarterly": 91, "biannual": 182, "annual": 365}
    days = freq_map.get(trad.get("frequency", "annual"), 365)
    await db.update_tradition(
        trad_id,
        last_held=now,
        next_held=now + timedelta(days=days),
        impact_score=min(100.0, trad.get("impact_score", 0) + 2.0),
    )
    return {"tradition": trad["name"], "held_at": now.isoformat()}


async def check_traditions(civ_id: str) -> list[dict]:
    traditions = await db.list_traditions(civ_id)
    now = datetime.now(timezone.utc)
    due = []
    for t in traditions:
        if t.get("next_held"):
            next_held = datetime.fromisoformat(t["next_held"])
            if next_held <= now:
                await hold_tradition(t["id"])
                due.append(t["name"])
    return due


def get_state() -> dict:
    return {"templates": [t["name"] for t in TRADITION_TEMPLATES], "initialized": True}
