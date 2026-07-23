import logging
import random

from app.federation import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.federation.knowledge")


class KnowledgeExchangeEngine:
    def __init__(self):
        self.stats = {"exchanges": 0, "technologies_shared": 0}

    async def share_knowledge(self, sender_civ_id: str, receiver_civ_id: str,
                              subject: str, content: str | None = None,
                              message_type: str = "knowledge_sharing") -> dict:
        msg_id = await db.create_message(
            sender_civilization_id=sender_civ_id,
            receiver_civilization_id=receiver_civ_id,
            sender_entity_type="research_lab",
            message_type=message_type, subject=subject, content=content,
        )
        self.stats["exchanges"] += 1
        await db.record_history(sender_civ_id, "knowledge_shared",
                                f"Shared knowledge: {subject}",
                                related_civilization_id=receiver_civ_id)
        await dispatch(Event(EventType.TECHNOLOGY_SHARED, {
            "sender_civilization_id": sender_civ_id,
            "receiver_civilization_id": receiver_civ_id,
            "subject": subject,
        }))
        return {"message_id": msg_id, "subject": subject}

    async def share_technology(self, sender_civ_id: str, receiver_civ_id: str,
                               tech_name: str) -> dict:
        self.stats["technologies_shared"] += 1
        msg_id = await db.create_message(
            sender_civilization_id=sender_civ_id,
            receiver_civilization_id=receiver_civ_id,
            sender_entity_type="research_lab",
            message_type="technology_transfer",
            subject=f"Technology: {tech_name}",
            content=f"Transferring technology {tech_name}",
        )
        await db.record_history(sender_civ_id, "technology_shared",
                                f"Shared technology: {tech_name}",
                                related_civilization_id=receiver_civ_id)
        return {"message_id": msg_id, "technology": tech_name}

    async def get_messages(self, civ_id: str, limit: int = 50) -> list[dict]:
        return await db.list_messages(civ_id, limit)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


knowledge_exchange_engine = KnowledgeExchangeEngine()
