import logging
import random
from datetime import datetime, timezone

from app.communication import persistence as comm_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.communication.social_graph")

RELATIONSHIP_TYPES = [
    "friend", "colleague", "manager", "employee",
    "partner", "competitor", "mentor", "client",
]


class SocialGraphEngine:
    def __init__(self):
        self.stats = {
            "connections_created": 0,
            "trust_updates": 0,
        }

    async def create_connection(self, entity_a_id: str, entity_a_type: str,
                                entity_b_id: str, entity_b_type: str,
                                relationship_type: str = "colleague",
                                trust_level: float = 50.0) -> dict:
        if relationship_type not in RELATIONSHIP_TYPES:
            relationship_type = "colleague"
        conn_id = await comm_db.save_social_connection(
            entity_a_id=entity_a_id,
            entity_a_type=entity_a_type,
            entity_b_id=entity_b_id,
            entity_b_type=entity_b_type,
            relationship_type=relationship_type,
            trust_level=trust_level,
        )
        self.stats["connections_created"] += 1

        await dispatch(Event(EventType.RELATIONSHIP_CREATED, {
            "connection_id": conn_id,
            "entity_a_id": entity_a_id,
            "entity_b_id": entity_b_id,
            "relationship_type": relationship_type,
            "trust_level": trust_level,
        }))

        return {
            "connection_id": conn_id,
            "relationship_type": relationship_type,
            "trust_level": trust_level,
            "status": "created",
        }

    async def get_network(self, entity_id: str) -> dict:
        connections = await comm_db.get_entity_connections(entity_id)
        trust_network = {
            "high_trust": [c for c in connections if c.get("trust_level", 0) >= 70],
            "medium_trust": [c for c in connections if 30 <= c.get("trust_level", 0) < 70],
            "low_trust": [c for c in connections if c.get("trust_level", 0) < 30],
        }
        relationship_summary = {}
        for c in connections:
            rtype = c.get("relationship_type", "unknown")
            if rtype not in relationship_summary:
                relationship_summary[rtype] = 0
            relationship_summary[rtype] += 1

        return {
            "entity_id": entity_id,
            "total_connections": len(connections),
            "connections": connections,
            "trust_network": trust_network,
            "relationship_summary": relationship_summary,
        }

    async def update_trust(self, entity_a_id: str, entity_a_type: str,
                           entity_b_id: str, entity_b_type: str,
                           change_amount: float, reason: str,
                           interaction_type: str) -> dict:
        connections = await comm_db.get_entity_connections(entity_a_id)
        current_trust = 50.0
        for c in connections:
            if c["other_id"] == entity_b_id:
                current_trust = c.get("trust_level", 50.0)
                break

        change_amount = max(-20.0, min(20.0, change_amount))
        new_trust = min(100.0, max(0.0, current_trust + change_amount))

        await comm_db.save_trust_record(
            entity_a_id=entity_a_id, entity_a_type=entity_a_type,
            entity_b_id=entity_b_id, entity_b_type=entity_b_type,
            change_amount=change_amount, reason=reason,
            interaction_type=interaction_type,
            previous_trust=current_trust,
        )

        await comm_db.save_social_connection(
            entity_a_id=entity_a_id, entity_a_type=entity_a_type,
            entity_b_id=entity_b_id, entity_b_type=entity_b_type,
            trust_level=new_trust,
        )
        self.stats["trust_updates"] += 1

        await dispatch(Event(EventType.TRUST_CHANGED, {
            "entity_a_id": entity_a_id,
            "entity_b_id": entity_b_id,
            "previous_trust": current_trust,
            "new_trust": new_trust,
            "change": change_amount,
            "reason": reason,
        }))

        return {
            "previous_trust": current_trust,
            "new_trust": new_trust,
            "change": change_amount,
            "reason": reason,
        }

    async def get_trust_history(self, entity_a_id: str, entity_b_id: str) -> list[dict]:
        return await comm_db.get_trust_history(entity_a_id, entity_b_id)

    async def calculate_influence_score(self, entity_id: str) -> float:
        connections = await comm_db.get_entity_connections(entity_id)
        if not connections:
            return 0.0
        total_trust = sum(c.get("trust_level", 0) for c in connections)
        avg_trust = total_trust / len(connections)
        high_trust_count = len([c for c in connections if c.get("trust_level", 0) >= 70])
        influence = min(100.0, avg_trust * 0.6 + high_trust_count * 5.0 + len(connections) * 2.0)
        return round(influence, 2)

    async def suggest_connections(self, entity_id: str) -> list[dict]:
        connections = await comm_db.get_entity_connections(entity_id)
        existing_ids = {c["other_id"] for c in connections}
        existing_ids.add(entity_id)
        suggestions = []
        for c in connections:
            if c.get("trust_level", 0) >= 60:
                other_connections = await comm_db.get_entity_connections(c["other_id"])
                for oc in other_connections:
                    if oc["other_id"] not in existing_ids:
                        suggestions.append({
                            "suggested_id": oc["other_id"],
                            "suggested_type": oc["other_type"],
                            "reason": f"Connected through {c['other_id']} (mutual connection)",
                            "mutual_connection_count": 1,
                        })
                        existing_ids.add(oc["other_id"])
        return suggestions[:10]

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "relationship_types": RELATIONSHIP_TYPES,
        }


social_graph = SocialGraphEngine()
