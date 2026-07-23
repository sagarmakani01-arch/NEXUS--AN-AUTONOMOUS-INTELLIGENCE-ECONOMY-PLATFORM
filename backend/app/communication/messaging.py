import json
import logging
from datetime import datetime, timezone

from app.communication import persistence as comm_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.communication.messaging")

MESSAGE_TYPES = ["private", "team", "public", "negotiation", "system"]
PRIORITY_LEVELS = ["low", "normal", "high", "urgent"]
ENTITY_TYPES = ["agent", "company", "organization", "human"]


class MessagingSystem:
    def __init__(self):
        self.stats = {
            "messages_sent": 0,
            "conversations_created": 0,
            "conversations_closed": 0,
        }

    async def send_message(self, sender_id: str, sender_type: str, receiver_id: str,
                           receiver_type: str, content: str, message_type: str = "private",
                           priority: str = "normal", conversation_id: str | None = None,
                           reply_to_id: str | None = None) -> dict:
        if message_type not in MESSAGE_TYPES:
            message_type = "private"
        if priority not in PRIORITY_LEVELS:
            priority = "normal"

        if not conversation_id and message_type in ("private", "team"):
            conv_participants = await comm_db.get_entity_conversations(sender_id)
            for conv in conv_participants:
                if conv.get("conversation_type") == message_type:
                    conv_detail = await comm_db.get_conversation(conv["id"])
                    if conv_detail:
                        part_ids = [p["participant_id"] for p in conv_detail.get("participants", [])]
                        if receiver_id in part_ids:
                            conversation_id = conv["id"]
                            break
            if not conversation_id:
                conv_id = await comm_db.create_conversation(
                    title=None,
                    topic=f"{message_type} conversation",
                    conversation_type=message_type,
                    participants=[
                        {"id": sender_id, "type": sender_type, "role": "member"},
                        {"id": receiver_id, "type": receiver_type, "role": "member"},
                    ],
                )
                conversation_id = conv_id
                self.stats["conversations_created"] += 1

        msg_id = await comm_db.save_message(
            sender_id=sender_id,
            sender_type=sender_type,
            receiver_id=receiver_id,
            receiver_type=receiver_type,
            content=content,
            message_type=message_type,
            priority=priority,
            conversation_id=conversation_id,
            reply_to_id=reply_to_id,
        )
        self.stats["messages_sent"] += 1

        await dispatch(Event(EventType.MESSAGE_SENT, {
            "message_id": msg_id,
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "message_type": message_type,
            "priority": priority,
        }))

        return {
            "message_id": msg_id,
            "conversation_id": conversation_id,
            "status": "sent",
        }

    async def get_conversation(self, conversation_id: str) -> dict | None:
        conv = await comm_db.get_conversation(conversation_id)
        if not conv:
            return None
        messages = await comm_db.get_conversation_messages(conversation_id, limit=50)
        conv["messages"] = messages
        return conv

    async def get_entity_inbox(self, entity_id: str) -> dict:
        conversations = await comm_db.get_entity_conversations(entity_id)
        messages = await comm_db.get_entity_messages(entity_id, limit=30)
        return {
            "conversations": conversations,
            "recent_messages": messages,
            "stats": self.stats,
        }

    async def search_messages(self, query: str, entity_id: str | None = None) -> list[dict]:
        return await comm_db.search_messages(query, entity_id)

    async def close_conversation(self, conversation_id: str, summary: str | None = None,
                                 decisions: str | None = None, outcome: str | None = None) -> bool:
        await comm_db.update_conversation_summary(conversation_id, summary or "", decisions, outcome)
        async with __import__("app.core.database", fromlist=["async_session_factory"]).async_session_factory() as session:
            from sqlalchemy import select
            from app.domain.models.message import Conversation
            result = await session.execute(select(Conversation).where(Conversation.id == conversation_id))
            conv = result.scalar_one_or_none()
            if conv:
                conv.status = "closed"
                conv.closed_at = datetime.now(timezone.utc)
                await session.commit()
                self.stats["conversations_closed"] += 1
                return True
        return False

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "message_types": MESSAGE_TYPES,
            "priority_levels": PRIORITY_LEVELS,
        }


messaging_system = MessagingSystem()
