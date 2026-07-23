import logging

from app.communication import persistence as comm_db
from app.communication.trust import trust_system

logger = logging.getLogger("nexus.communication.intelligence")


class CommunicationIntelligence:
    def __init__(self):
        self.stats = {
            "analyses_performed": 0,
            "recommendations_generated": 0,
        }

    async def analyze_communication_context(self, sender_id: str, receiver_id: str) -> dict:
        trust_assessment = await trust_system.get_trust_assessment(sender_id, receiver_id)
        connections = await comm_db.get_entity_connections(sender_id)
        receiver_connection = None
        for c in connections:
            if c["other_id"] == receiver_id:
                receiver_connection = c
                break

        relationship_type = receiver_connection.get("relationship_type", "unknown") if receiver_connection else "none"
        trust_level = trust_assessment.get("trust_level", 50.0)

        communication_strategy = self._determine_strategy(relationship_type, trust_level)
        self.stats["analyses_performed"] += 1

        return {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "relationship_type": relationship_type,
            "trust_level": trust_level,
            "trust_trend": trust_assessment.get("trend", "stable"),
            "recommended_strategy": communication_strategy,
            "affects": trust_assessment.get("affects", {}),
        }

    def _determine_strategy(self, relationship_type: str, trust_level: float) -> dict:
        if trust_level >= 70 and relationship_type in ("friend", "mentor", "partner"):
            return {
                "tone": "friendly",
                "detail_level": "high",
                "formality": "casual",
                "approach": "Direct and open communication",
            }
        elif trust_level >= 50 and relationship_type in ("colleague", "employee"):
            return {
                "tone": "professional",
                "detail_level": "medium",
                "formality": "formal",
                "approach": "Clear and respectful communication",
            }
        elif trust_level >= 30:
            return {
                "tone": "neutral",
                "detail_level": "medium",
                "formality": "formal",
                "approach": "Cautious and measured communication",
            }
        else:
            return {
                "tone": "guarded",
                "detail_level": "low",
                "formality": "very_formal",
                "approach": "Minimal information sharing, focus on facts",
            }

    async def get_agent_social_intelligence(self, entity_id: str) -> dict:
        connections = await comm_db.get_entity_connections(entity_id)
        if not connections:
            return {
                "entity_id": entity_id,
                "social_capital": 0.0,
                "network_diversity": 0.0,
                "influence_score": 0.0,
                "communication_effectiveness": 0.0,
            }

        total_trust = sum(c.get("trust_level", 0) for c in connections)
        avg_trust = total_trust / len(connections)
        high_trust = len([c for c in connections if c.get("trust_level", 0) >= 70])

        social_capital = min(100.0, avg_trust * 0.4 + high_trust * 8.0 + len(connections) * 1.5)

        relationship_types = set(c.get("relationship_type", "") for c in connections)
        network_diversity = min(100.0, len(relationship_types) * 12.5)

        influence = min(100.0, social_capital * 0.3 + network_diversity * 0.3 + high_trust * 5.0)
        effectiveness = min(100.0, avg_trust * 0.5 + len(connections) * 2.0 + high_trust * 3.0)

        self.stats["recommendations_generated"] += 1

        return {
            "entity_id": entity_id,
            "social_capital": round(social_capital, 2),
            "network_diversity": round(network_diversity, 2),
            "influence_score": round(influence, 2),
            "communication_effectiveness": round(effectiveness, 2),
            "total_connections": len(connections),
            "high_trust_connections": high_trust,
            "relationship_types": list(relationship_types),
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


communication_intelligence = CommunicationIntelligence()
