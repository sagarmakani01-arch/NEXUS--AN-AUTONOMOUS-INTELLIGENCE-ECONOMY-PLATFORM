import json
import logging
import random

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.diffusion")

SHARING_MODES = {
    "teaching": {"knowledge_spread": 0.3, "reputation_gain": 0.05, "cost": 5},
    "mentorship": {"knowledge_spread": 0.5, "reputation_gain": 0.1, "cost": 10},
    "publication": {"knowledge_spread": 0.8, "reputation_gain": 0.15, "cost": 20},
    "conference": {"knowledge_spread": 0.6, "reputation_gain": 0.12, "cost": 30},
    "collaboration": {"knowledge_spread": 0.4, "reputation_gain": 0.08, "cost": 8},
}

VISIBILITY_LEVELS = {
    "public": {"spread_multiplier": 1.5, "proprietary_risk": 1.0},
    "restricted": {"spread_multiplier": 1.0, "proprietary_risk": 0.5},
    "confidential": {"spread_multiplier": 0.5, "proprietary_risk": 0.2},
    "proprietary": {"spread_multiplier": 0.2, "proprietary_risk": 0.0},
}


class KnowledgeDiffusionEngine:
    def __init__(self):
        self.stats = {
            "knowledge_shared": 0,
            "publications_spread": 0,
            "conferences_held": 0,
            "teaching_sessions": 0,
        }

    async def share_knowledge(self, source_agent_id: str, target_agent_id: str,
                              knowledge_node_ids: list[str],
                              mode: str = "collaboration",
                              visibility: str = "public") -> dict:
        config = SHARING_MODES.get(mode, SHARING_MODES["collaboration"])
        vis_config = VISIBILITY_LEVELS.get(visibility, VISIBILITY_LEVELS["public"])

        nodes_shared = []
        for node_id in knowledge_node_ids:
            node = await db.get_knowledge_node(node_id)
            if node:
                new_usage = node.get("usage_count", 0) + 1
                await db.update_knowledge_node(node_id, usage_count=new_usage)
                nodes_shared.append(node_id)

        self.stats["knowledge_shared"] += len(nodes_shared)

        if mode == "publication":
            self.stats["publications_spread"] += 1
        elif mode == "teaching":
            self.stats["teaching_sessions"] += 1

        return {
            "success": True, "nodes_shared": len(nodes_shared),
            "mode": mode, "visibility": visibility,
            "spread_factor": config["knowledge_spread"] * vis_config["spread_multiplier"],
        }

    async def hold_conference(self, name: str, domain: str | None = None,
                              organizer_id: str | None = None) -> dict:
        conf_id = await db.create_conference(
            name=name, domain=domain, organizer_id=organizer_id,
            conference_type=random.choice(["virtual", "hybrid", "in_person"]),
            attendee_count=random.randint(10, 200),
            paper_count=random.randint(5, 50),
            reputation_impact=random.uniform(0.05, 0.2),
        )
        self.stats["conferences_held"] += 1
        return {"conference_id": conf_id, "name": name, "domain": domain}

    async def get_diffusion_stats(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "sharing_modes": SHARING_MODES,
            "visibility_levels": list(VISIBILITY_LEVELS.keys()),
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


knowledge_diffusion_engine = KnowledgeDiffusionEngine()
