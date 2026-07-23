import logging
import random

from app.federation import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.federation.migration")

MIGRATION_REASONS = [
    "job_opportunities", "quality_of_life", "resources",
    "government_policy", "economic_conditions", "education",
    "safety", "family", "adventure",
]


class MigrationEngine:
    def __init__(self):
        self.stats = {"migrations": 0, "total_skill_value": 0}

    async def process_migration(self, agent_id: str, origin_civ_id: str,
                                destination_civ_id: str,
                                reason: str | None = None) -> dict:
        reason = reason or random.choice(MIGRATION_REASONS)
        skill_value = round(random.uniform(1, 10), 1)
        resource_bringing = round(random.uniform(0, 50), 1)

        migration_id = await db.create_migration(
            agent_id=agent_id,
            origin_civilization_id=origin_civ_id,
            destination_civilization_id=destination_civ_id,
            reason=reason, skill_value=skill_value,
            resource_bringing=resource_bringing,
        )

        origin = await db.get_civilization(origin_civ_id)
        dest = await db.get_civilization(destination_civ_id)
        if origin:
            await db.update_civilization(origin_civ_id,
                                         population=max(0, origin["population"] - 1))
        if dest:
            await db.update_civilization(destination_civ_id,
                                         population=dest["population"] + 1)

        self.stats["migrations"] += 1
        self.stats["total_skill_value"] += skill_value

        await db.record_history(origin_civ_id, "migration_out",
                                f"Agent migrated to {dest['name'] if dest else 'unknown'}",
                                related_civilization_id=destination_civ_id)
        await db.record_history(destination_civ_id, "migration_in",
                                f"Agent migrated from {origin['name'] if origin else 'unknown'}",
                                related_civilization_id=origin_civ_id)
        await dispatch(Event(EventType.MIGRATION_STARTED, {
            "agent_id": agent_id, "origin": origin_civ_id,
            "destination": destination_civ_id, "reason": reason,
        }))
        return {"migration_id": migration_id, "reason": reason,
                "skill_value": skill_value}

    async def evaluate_migration_pull(self, civ_id: str) -> dict:
        civ = await db.get_civilization(civ_id)
        if not civ:
            return {"pull_score": 0}
        pull = (civ["economic_power"] * 0.3 + civ["happiness"] * 0.3 +
                civ["technology_level"] * 10 * 0.2 + civ["reputation"] * 0.2)
        return {"pull_score": round(pull, 1), "population": civ["population"]}

    async def list_migrations(self, civ_id: str | None = None) -> list[dict]:
        return await db.list_migrations(civ_id)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


migration_engine = MigrationEngine()
