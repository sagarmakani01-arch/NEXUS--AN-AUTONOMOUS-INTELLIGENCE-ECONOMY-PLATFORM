import logging
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.memory")


async def record_memory(civ_id: str, event_type: str, title: str,
                        description: str | None = None, impact: float = 50.0) -> dict:
    mid = await db.create_collective_memory(
        civilization_id=civ_id,
        event_type=event_type,
        title=title,
        description=description,
        impact_score=impact,
    )
    return {"id": mid, "title": title, "event_type": event_type}


async def record_major_event(civ_id: str, event_type: str, title: str,
                             description: str | None = None, impact: float = 50.0) -> dict:
    result = await record_memory(civ_id, event_type, title, description, impact)
    await db.create_cultural_timeline(
        civilization_id=civ_id,
        change_type=event_type,
        description=title,
        cause="historical_event",
        impact_score=impact,
    )
    return result


async def get_memories(civ_id: str, event_type: str | None = None,
                       limit: int = 50) -> list[dict]:
    return await db.list_collective_memories(civ_id, event_type=event_type, limit=limit)


async def get_memories_by_impact(civ_id: str, min_impact: float = 50.0,
                                 limit: int = 20) -> list[dict]:
    all_mems = await db.list_collective_memories(civ_id, limit=200)
    return [m for m in all_mems if m["impact_score"] >= min_impact][:limit]


def get_state() -> dict:
    return {"initialized": True}
