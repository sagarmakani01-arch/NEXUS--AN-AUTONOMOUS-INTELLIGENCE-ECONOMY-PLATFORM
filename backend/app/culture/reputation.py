import logging
import random
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.reputation")


async def record_contribution(civ_id: str, entity_id: str, entity_type: str = "agent",
                              influence_delta: float = 5.0) -> dict:
    entries = await db.list_reputation_entries(civ_id, entity_type=entity_type)
    existing = next((e for e in entries if e["entity_id"] == entity_id), None)

    if existing:
        new_influence = min(1000.0, existing["influence_score"] + influence_delta)
        new_count = existing["contribution_count"] + 1
        engagement = min(100.0, existing["sustained_engagement"] + 1.0)
        await db.update_social_dynamics(civ_id)  # touch
        # We need a direct update approach
        from sqlalchemy import select
        from app.core.database import async_session_factory
        from app.domain.models.culture import ReputationEntry
        async with async_session_factory() as session:
            r = await session.execute(select(ReputationEntry).where(ReputationEntry.id == existing["id"]))
            o = r.scalar_one_or_none()
            if o:
                o.influence_score = new_influence
                o.contribution_count = new_count
                o.sustained_engagement = engagement
                await session.commit()
        return {"entity_id": entity_id, "influence": new_influence, "contributions": new_count}
    else:
        eid = await db.create_reputation_entry(
            civilization_id=civ_id,
            entity_id=entity_id,
            entity_type=entity_type,
            influence_score=influence_delta,
            contribution_count=1,
            sustained_engagement=1.0,
        )
        return {"entity_id": entity_id, "influence": influence_delta, "contributions": 1}


async def get_rankings(civ_id: str, entity_type: str | None = None,
                       limit: int = 20) -> list[dict]:
    return await db.list_reputation_entries(civ_id, entity_type=entity_type, limit=limit)


async def get_entity_influence(civ_id: str, entity_id: str) -> float:
    entries = await db.list_reputation_entries(civ_id)
    entry = next((e for e in entries if e["entity_id"] == entity_id), None)
    return entry["influence_score"] if entry else 0.0


def get_state() -> dict:
    return {"initialized": True}
