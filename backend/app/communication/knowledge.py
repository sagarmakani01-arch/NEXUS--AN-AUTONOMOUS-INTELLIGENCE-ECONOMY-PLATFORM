import json
import logging

from app.communication import persistence as comm_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.communication.knowledge")

KNOWLEDGE_TYPES = [
    "skill", "document", "research", "strategy",
    "market_info", "technical", "experience", "best_practice",
]
VISIBILITY_LEVELS = ["private", "team", "company", "public"]


class KnowledgeExchange:
    def __init__(self):
        self.stats = {
            "knowledge_shared": 0,
            "knowledge_accessed": 0,
        }

    async def share_knowledge(self, owner_id: str, owner_type: str, knowledge_type: str,
                              title: str, content: str, visibility: str = "private",
                              tags: list[str] | None = None) -> dict:
        if knowledge_type not in KNOWLEDGE_TYPES:
            knowledge_type = "technical"
        if visibility not in VISIBILITY_LEVELS:
            visibility = "private"

        ks_id = await comm_db.save_knowledge(
            owner_id=owner_id,
            owner_type=owner_type,
            knowledge_type=knowledge_type,
            title=title,
            content=content,
            visibility=visibility,
            tags=tags,
        )
        self.stats["knowledge_shared"] += 1

        await dispatch(Event(EventType.KNOWLEDGE_SHARED, {
            "knowledge_id": ks_id,
            "owner_id": owner_id,
            "knowledge_type": knowledge_type,
            "visibility": visibility,
        }))

        return {
            "knowledge_id": ks_id,
            "status": "shared",
            "visibility": visibility,
        }

    async def search_knowledge(self, query: str | None = None, knowledge_type: str | None = None,
                               visibility: str | None = None) -> list[dict]:
        return await comm_db.search_knowledge(query, knowledge_type, visibility)

    async def access_knowledge(self, knowledge_id: str) -> dict | None:
        result = await comm_db.access_knowledge(knowledge_id)
        if result:
            self.stats["knowledge_accessed"] += 1
        return result

    async def get_entity_knowledge(self, entity_id: str) -> dict:
        private_knowledge = await comm_db.search_knowledge(visibility="private")
        private_knowledge = [k for k in private_knowledge if k.get("owner_id") == entity_id]
        team_knowledge = await comm_db.search_knowledge(visibility="team")
        public_knowledge = await comm_db.search_knowledge(visibility="public")
        return {
            "entity_id": entity_id,
            "private_knowledge": private_knowledge,
            "team_knowledge": team_knowledge[:20],
            "public_knowledge": public_knowledge[:20],
            "stats": {
                "private_count": len(private_knowledge),
                "team_count": len(team_knowledge),
                "public_count": len(public_knowledge),
            },
        }

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "knowledge_types": KNOWLEDGE_TYPES,
            "visibility_levels": VISIBILITY_LEVELS,
        }


knowledge_exchange = KnowledgeExchange()
