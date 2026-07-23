import logging
import random
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.development")

STAGES = ["concept", "prototype", "testing", "early_adoption", "mature", "obsolete"]
STAGE_ORDER = {s: i for i, s in enumerate(STAGES)}


async def advance_development(dev_id: str) -> dict | None:
    dev = (await db.list_developments())[0] if False else None
    devs = await db.list_developments()
    dev = next((d for d in devs if d["id"] == dev_id), None)
    if not dev:
        return None

    current_idx = STAGE_ORDER.get(dev["stage"], 0)
    if current_idx >= len(STAGES) - 1:
        return {"status": "already_obsolete"}

    progress = dev["progress"] + random.uniform(5.0, 20.0)
    if progress >= 100.0:
        next_stage = STAGES[current_idx + 1]
        await db.update_development(dev_id, stage=next_stage, progress=0.0)
        await db.create_timeline_event(
            civilization_id=dev["civilization_id"],
            event_type="development_stage_changed",
            technology_id=dev["technology_id"],
            title=f"Advanced to {next_stage}",
            impact_score=10.0,
        )
        return {"new_stage": next_stage, "technology_id": dev["technology_id"]}
    else:
        await db.update_development(dev_id, progress=progress)
        return {"progress": progress}


async def start_development(civ_id: str, tech_id: str, lead_agent_id: str | None = None) -> dict:
    dev_id = await db.create_development(
        technology_id=tech_id,
        civilization_id=civ_id,
        stage="concept",
        progress=0.0,
        lead_agent_id=lead_agent_id,
    )
    await db.create_timeline_event(
        civilization_id=civ_id,
        event_type="development_started",
        technology_id=tech_id,
        title="Technology development started",
        impact_score=5.0,
    )
    return {"id": dev_id, "stage": "concept"}


def get_state() -> dict:
    return {"stages": STAGES, "initialized": True}
