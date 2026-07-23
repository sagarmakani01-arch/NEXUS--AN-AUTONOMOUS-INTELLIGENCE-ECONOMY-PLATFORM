import json
import logging
import random

from app.federation import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.federation.diplomacy")

RELATION_STATUSES = {
    "neutral": {"level_range": (40, 60), "trust_range": (40, 60)},
    "friendly": {"level_range": (60, 80), "trust_range": (60, 80)},
    "partner": {"level_range": (75, 95), "trust_range": (70, 95)},
    "competitive": {"level_range": (30, 50), "trust_range": (20, 50)},
    "hostile": {"level_range": (5, 30), "trust_range": (5, 30)},
}

DIPLOMATIC_ACTIONS = ["agreement", "alliance", "trade_deal", "research_partnership", "conflict_resolution"]


class DiplomacyEngine:
    def __init__(self):
        self.stats = {"relations_formed": 0, "agreements_made": 0, "conflicts_started": 0}

    async def establish_relation(self, civ_a_id: str, civ_b_id: str,
                                 initial_status: str = "neutral") -> dict:
        existing = await db.get_diplomatic_relation(civ_a_id, civ_b_id)
        if existing:
            return {"success": False, "error": "Relation exists"}

        config = RELATION_STATUSES.get(initial_status, RELATION_STATUSES["neutral"])
        rel_id = await db.create_diplomatic_relation(
            civ_a_id, civ_b_id,
            relation_level=random.uniform(*config["level_range"]),
            status=initial_status,
            trust_score=random.uniform(*config["trust_range"]),
        )
        self.stats["relations_formed"] += 1

        await db.record_history(civ_a_id, "diplomacy",
                                f"Established {initial_status} relations",
                                related_civilization_id=civ_b_id)
        await db.record_history(civ_b_id, "diplomacy",
                                f"Established {initial_status} relations",
                                related_civilization_id=civ_a_id)

        return {"relation_id": rel_id, "status": initial_status}

    async def update_relation(self, civ_a_id: str, civ_b_id: str,
                              new_status: str) -> dict:
        rel_data = await db.get_diplomatic_relation(civ_a_id, civ_b_id)
        if not rel_data:
            return {"success": False, "error": "No relation found"}

        config = RELATION_STATUSES.get(new_status, RELATION_STATUSES["neutral"])
        await db.update_diplomatic_relation(
            rel_data["id"],
            status=new_status,
            relation_level=random.uniform(*config["level_range"]),
            trust_score=random.uniform(*config["trust_range"]),
        )

        if new_status == "hostile":
            self.stats["conflicts_started"] += 1

        await db.record_history(civ_a_id, "diplomatic_change",
                                f"Relations changed to {new_status}",
                                related_civilization_id=civ_b_id)
        await dispatch(Event(EventType.DIPLOMATIC_CHANGE, {
            "civilization_a_id": civ_a_id, "civilization_b_id": civ_b_id,
            "new_status": new_status,
        }))
        return {"success": True, "new_status": new_status}

    async def conduct_action(self, civ_a_id: str, civ_b_id: str,
                             action: str) -> dict:
        self.stats["agreements_made"] += 1
        await db.record_history(civ_a_id, action,
                                f"Conducted {action} with another civilization",
                                related_civilization_id=civ_b_id)
        return {"success": True, "action": action}

    async def get_relation(self, civ_a_id: str, civ_b_id: str) -> dict | None:
        return await db.get_diplomatic_relation(civ_a_id, civ_b_id)

    async def list_relations(self, civ_id: str | None = None) -> list[dict]:
        return await db.list_diplomatic_relations(civ_id)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


diplomacy_engine = DiplomacyEngine()
