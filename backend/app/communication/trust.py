import logging
from datetime import datetime, timezone

from app.communication import persistence as comm_db
from app.communication.social_graph import social_graph
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.communication.trust")

TRUST_CHANGE_REASONS = {
    "collaboration": {"amount": 5.0, "description": "Successful collaboration"},
    "conflict": {"amount": -8.0, "description": "Disagreement or conflict"},
    "honest_dealing": {"amount": 3.0, "description": "Honest and transparent transaction"},
    "broken_agreement": {"amount": -12.0, "description": "Failed to honor agreement"},
    "positive_outcome": {"amount": 4.0, "description": "Achieved positive result together"},
    "negative_outcome": {"amount": -6.0, "description": "Joint effort failed"},
    "knowledge_share": {"amount": 2.0, "description": "Shared valuable knowledge"},
    "mentorship": {"amount": 3.0, "description": "Provided mentorship and guidance"},
    "reliability": {"amount": 2.0, "description": "Consistent and reliable behavior"},
    "unreliability": {"amount": -5.0, "description": "Failed to meet commitments"},
}


class TrustSystem:
    def __init__(self):
        self.stats = {
            "trust_updates": 0,
            "trust_recoveries": 0,
            "trust_declines": 0,
        }

    async def process_interaction(self, entity_a_id: str, entity_a_type: str,
                                  entity_b_id: str, entity_b_type: str,
                                  interaction_type: str) -> dict:
        reason_config = TRUST_CHANGE_REASONS.get(interaction_type)
        if not reason_config:
            return {"changed": False, "reason": "Unknown interaction type"}

        change_amount = reason_config["amount"]
        connections = await comm_db.get_entity_connections(entity_a_id)
        current_trust = 50.0
        for c in connections:
            if c["other_id"] == entity_b_id:
                current_trust = c.get("trust_level", 50.0)
                break

        result = await social_graph.update_trust(
            entity_a_id=entity_a_id,
            entity_a_type=entity_a_type,
            entity_b_id=entity_b_id,
            entity_b_type=entity_b_type,
            change_amount=change_amount,
            reason=reason_config["description"],
            interaction_type=interaction_type,
        )
        self.stats["trust_updates"] += 1
        if change_amount > 0:
            self.stats["trust_recoveries"] += 1
        else:
            self.stats["trust_declines"] += 1

        return {
            "changed": True,
            "previous_trust": result["previous_trust"],
            "new_trust": result["new_trust"],
            "change": change_amount,
            "reason": reason_config["description"],
            "interaction_type": interaction_type,
        }

    async def get_trust_assessment(self, entity_a_id: str, entity_b_id: str) -> dict:
        connections = await comm_db.get_entity_connections(entity_a_id)
        current_trust = 50.0
        for c in connections:
            if c["other_id"] == entity_b_id:
                current_trust = c.get("trust_level", 50.0)
                break

        history = await comm_db.get_trust_history(entity_a_id, entity_b_id)
        trend = "stable"
        if len(history) >= 2:
            recent_changes = [h.get("change_amount", 0) for h in history[:3]]
            avg_change = sum(recent_changes) / len(recent_changes)
            if avg_change > 1:
                trend = "improving"
            elif avg_change < -1:
                trend = "declining"

        level = "low"
        if current_trust >= 70:
            level = "high"
        elif current_trust >= 40:
            level = "medium"

        hiring_trust = current_trust >= 60
        partnership_trust = current_trust >= 50
        information_sharing = current_trust >= 40
        negotiation_willingness = current_trust >= 30

        return {
            "entity_a_id": entity_a_id,
            "entity_b_id": entity_b_id,
            "trust_level": round(current_trust, 2),
            "trust_level_label": level,
            "trend": trend,
            "total_interactions": len(history),
            "affects": {
                "hiring": hiring_trust,
                "partnership": partnership_trust,
                "information_sharing": information_sharing,
                "negotiation_willingness": negotiation_willingness,
            },
            "history": history[:5],
        }

    async def get_entity_trust_overview(self, entity_id: str) -> dict:
        connections = await comm_db.get_entity_connections(entity_id)
        if not connections:
            return {
                "entity_id": entity_id,
                "average_trust": 0.0,
                "highest_trust": None,
                "lowest_trust": None,
                "trusted_partners": 0,
                "distrusted_partners": 0,
            }

        trusts = [c.get("trust_level", 0) for c in connections]
        avg_trust = sum(trusts) / len(trusts)
        highest = max(connections, key=lambda c: c.get("trust_level", 0))
        lowest = min(connections, key=lambda c: c.get("trust_level", 0))

        return {
            "entity_id": entity_id,
            "average_trust": round(avg_trust, 2),
            "highest_trust": {
                "entity_id": highest["other_id"],
                "trust_level": highest.get("trust_level", 0),
            },
            "lowest_trust": {
                "entity_id": lowest["other_id"],
                "trust_level": lowest.get("trust_level", 0),
            },
            "trusted_partners": len([t for t in trusts if t >= 70]),
            "distrusted_partners": len([t for t in trusts if t < 30]),
            "total_connections": len(connections),
        }

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "trust_change_reasons": list(TRUST_CHANGE_REASONS.keys()),
        }


trust_system = TrustSystem()
