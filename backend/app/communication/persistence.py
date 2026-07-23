import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_, or_

from app.core.database import async_session_factory
from app.domain.models.message import Message, Conversation, ConversationParticipant, KnowledgeShare
from app.domain.models.social import SocialConnection, Community, CommunityMember, TrustRecord
from app.domain.models.relationship import Relationship

logger = logging.getLogger("nexus.communication")


async def save_message(sender_id: str, sender_type: str, receiver_id: str, receiver_type: str,
                       content: str, message_type: str = "private", priority: str = "normal",
                       conversation_id: str | None = None, reply_to_id: str | None = None,
                       metadata: dict | None = None) -> str:
    async with async_session_factory() as session:
        msg = Message(
            sender_id=sender_id,
            sender_type=sender_type,
            receiver_id=receiver_id,
            receiver_type=receiver_type,
            message_type=message_type,
            content=content,
            priority=priority,
            conversation_id=conversation_id,
            reply_to_id=reply_to_id,
            metadata_json=json.dumps(metadata or {}),
        )
        session.add(msg)
        await session.commit()
        if conversation_id:
            conv_result = await session.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conv = conv_result.scalar_one_or_none()
            if conv:
                conv.message_count = (conv.message_count or 0) + 1
                conv.updated_at = datetime.now(timezone.utc)
                await session.commit()
        return msg.id


async def get_conversation_messages(conversation_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        messages = result.scalars().all()
        return [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "sender_type": m.sender_type,
                "receiver_id": m.receiver_id,
                "receiver_type": m.receiver_type,
                "conversation_id": m.conversation_id,
                "message_type": m.message_type,
                "content": m.content,
                "priority": m.priority,
                "status": m.status,
                "reply_to_id": m.reply_to_id,
                "metadata_json": m.metadata_json,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "read_at": m.read_at.isoformat() if m.read_at else None,
            }
            for m in messages
        ]


async def get_entity_messages(entity_id: str, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Message)
            .where(or_(Message.sender_id == entity_id, Message.receiver_id == entity_id))
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()
        return [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "sender_type": m.sender_type,
                "receiver_id": m.receiver_id,
                "receiver_type": m.receiver_type,
                "conversation_id": m.conversation_id,
                "message_type": m.message_type,
                "content": m.content,
                "priority": m.priority,
                "status": m.status,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]


async def search_messages(query: str, entity_id: str | None = None, limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Message).where(Message.content.contains(query))
        if entity_id:
            stmt = stmt.where(or_(Message.sender_id == entity_id, Message.receiver_id == entity_id))
        stmt = stmt.order_by(Message.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        messages = result.scalars().all()
        return [
            {
                "id": m.id,
                "sender_id": m.sender_id,
                "receiver_id": m.receiver_id,
                "content": m.content,
                "message_type": m.message_type,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ]


async def create_conversation(title: str | None, topic: str | None, conversation_type: str = "private",
                               participants: list[dict] | None = None, summary: str | None = None) -> str:
    async with async_session_factory() as session:
        conv = Conversation(
            title=title,
            topic=topic,
            conversation_type=conversation_type,
            summary=summary,
        )
        session.add(conv)
        await session.flush()
        conv_id = conv.id
        if participants:
            for p in participants:
                cp = ConversationParticipant(
                    conversation_id=conv_id,
                    participant_id=p.get("id", ""),
                    participant_type=p.get("type", "agent"),
                    role=p.get("role", "member"),
                )
                session.add(cp)
        await session.commit()
        return conv_id


async def get_conversation(conversation_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = result.scalar_one_or_none()
        if not conv:
            return None
        parts_result = await session.execute(
            select(ConversationParticipant).where(ConversationParticipant.conversation_id == conversation_id)
        )
        parts = parts_result.scalars().all()
        return {
            "id": conv.id,
            "title": conv.title,
            "topic": conv.topic,
            "conversation_type": conv.conversation_type,
            "summary": conv.summary,
            "decisions": conv.decisions,
            "outcome": conv.outcome,
            "status": conv.status,
            "message_count": conv.message_count,
            "participants": [
                {
                    "id": p.id,
                    "participant_id": p.participant_id,
                    "participant_type": p.participant_type,
                    "role": p.role,
                    "notification_count": p.notification_count,
                }
                for p in parts
            ],
            "created_at": conv.created_at.isoformat() if conv.created_at else None,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
        }


async def get_entity_conversations(entity_id: str) -> list[dict]:
    async with async_session_factory() as session:
        parts_result = await session.execute(
            select(ConversationParticipant)
            .where(ConversationParticipant.participant_id == entity_id)
            .where(ConversationParticipant.status == "active")
        )
        parts = parts_result.scalars().all()
        conv_ids = [p.conversation_id for p in parts]
        if not conv_ids:
            return []
        conv_result = await session.execute(
            select(Conversation).where(Conversation.id.in_(conv_ids))
            .order_by(Conversation.updated_at.desc())
        )
        convs = conv_result.scalars().all()
        return [
            {
                "id": c.id,
                "title": c.title,
                "topic": c.topic,
                "conversation_type": c.conversation_type,
                "message_count": c.message_count,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in convs
        ]


async def update_conversation_summary(conversation_id: str, summary: str, decisions: str | None = None,
                                      outcome: str | None = None) -> None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conv = result.scalar_one_or_none()
        if conv:
            conv.summary = summary
            if decisions:
                conv.decisions = decisions
            if outcome:
                conv.outcome = outcome
            conv.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def save_social_connection(entity_a_id: str, entity_a_type: str, entity_b_id: str,
                                 entity_b_type: str, relationship_type: str = "colleague",
                                 trust_level: float = 50.0) -> str:
    async with async_session_factory() as session:
        a_id, b_id = sorted([entity_a_id, entity_b_id])
        a_type = entity_a_type if entity_a_id == a_id else entity_b_type
        b_type = entity_b_type if entity_b_id == b_id else entity_a_type
        result = await session.execute(
            select(SocialConnection).where(
                and_(SocialConnection.entity_a_id == a_id, SocialConnection.entity_b_id == b_id)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.interaction_count += 1
            existing.last_interaction_at = datetime.now(timezone.utc)
            existing.trust_level = min(100.0, max(0.0, trust_level))
            await session.commit()
            return existing.id
        conn = SocialConnection(
            entity_a_id=a_id, entity_a_type=a_type,
            entity_b_id=b_id, entity_b_type=b_type,
            relationship_type=relationship_type,
            trust_level=trust_level,
            interaction_count=1,
            last_interaction_at=datetime.now(timezone.utc),
        )
        session.add(conn)
        await session.commit()
        return conn.id


async def get_entity_connections(entity_id: str) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(SocialConnection).where(
                or_(SocialConnection.entity_a_id == entity_id, SocialConnection.entity_b_id == entity_id)
            ).order_by(SocialConnection.relationship_strength.desc())
        )
        conns = result.scalars().all()
        connections = []
        for c in conns:
            other_id = c.entity_b_id if c.entity_a_id == entity_id else c.entity_a_id
            other_type = c.entity_b_type if c.entity_a_id == entity_id else c.entity_a_type
            connections.append({
                "id": c.id,
                "other_id": other_id,
                "other_type": other_type,
                "relationship_type": c.relationship_type,
                "trust_level": c.trust_level,
                "relationship_strength": c.relationship_strength,
                "interaction_count": c.interaction_count,
                "shared_knowledge_count": c.shared_knowledge_count,
                "sentiment_score": c.sentiment_score,
                "last_interaction_at": c.last_interaction_at.isoformat() if c.last_interaction_at else None,
            })
        return connections


async def save_trust_record(entity_a_id: str, entity_a_type: str, entity_b_id: str,
                             entity_b_type: str, change_amount: float, reason: str,
                             interaction_type: str, previous_trust: float) -> str:
    async with async_session_factory() as session:
        new_trust = min(100.0, max(0.0, previous_trust + change_amount))
        record = TrustRecord(
            entity_a_id=entity_a_id, entity_a_type=entity_a_type,
            entity_b_id=entity_b_id, entity_b_type=entity_b_type,
            change_amount=change_amount, reason=reason,
            interaction_type=interaction_type,
            previous_trust=previous_trust, new_trust=new_trust,
        )
        session.add(record)
        await session.commit()
        return record.id


async def get_trust_history(entity_a_id: str, entity_b_id: str, limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(TrustRecord).where(
                or_(
                    and_(TrustRecord.entity_a_id == entity_a_id, TrustRecord.entity_b_id == entity_b_id),
                    and_(TrustRecord.entity_a_id == entity_b_id, TrustRecord.entity_b_id == entity_a_id),
                )
            ).order_by(TrustRecord.created_at.desc()).limit(limit)
        )
        records = result.scalars().all()
        return [
            {
                "id": r.id,
                "change_amount": r.change_amount,
                "reason": r.reason,
                "interaction_type": r.interaction_type,
                "previous_trust": r.previous_trust,
                "new_trust": r.new_trust,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in records
        ]


async def save_knowledge(owner_id: str, owner_type: str, knowledge_type: str, title: str,
                         content: str, visibility: str = "private", tags: list[str] | None = None) -> str:
    async with async_session_factory() as session:
        ks = KnowledgeShare(
            owner_id=owner_id, owner_type=owner_type,
            knowledge_type=knowledge_type, title=title,
            content=content, visibility=visibility,
            tags=json.dumps(tags or []),
        )
        session.add(ks)
        await session.commit()
        return ks.id


async def search_knowledge(query: str | None = None, knowledge_type: str | None = None,
                           visibility: str | None = None, limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(KnowledgeShare)
        conditions = []
        if query:
            conditions.append(KnowledgeShare.title.contains(query))
        if knowledge_type:
            conditions.append(KnowledgeShare.knowledge_type == knowledge_type)
        if visibility:
            conditions.append(KnowledgeShare.visibility == visibility)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(KnowledgeShare.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return [
            {
                "id": k.id,
                "owner_id": k.owner_id,
                "owner_type": k.owner_type,
                "knowledge_type": k.knowledge_type,
                "title": k.title,
                "content": k.content,
                "visibility": k.visibility,
                "tags": json.loads(k.tags) if k.tags else [],
                "access_count": k.access_count,
                "rating": k.rating,
                "created_at": k.created_at.isoformat() if k.created_at else None,
            }
            for k in items
        ]


async def access_knowledge(knowledge_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(KnowledgeShare).where(KnowledgeShare.id == knowledge_id)
        )
        ks = result.scalar_one_or_none()
        if not ks:
            return None
        ks.access_count = (ks.access_count or 0) + 1
        ks.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return {
            "id": ks.id,
            "owner_id": ks.owner_id,
            "knowledge_type": ks.knowledge_type,
            "title": ks.title,
            "content": ks.content,
            "visibility": ks.visibility,
            "tags": json.loads(ks.tags) if ks.tags else [],
            "access_count": ks.access_count,
            "rating": ks.rating,
        }


async def create_community(name: str, description: str | None, community_type: str = "open",
                           purpose: str | None = None, industry: str | None = None,
                           founded_by: str | None = None) -> str:
    async with async_session_factory() as session:
        comm = Community(
            name=name, description=description,
            community_type=community_type, purpose=purpose,
            industry=industry, founded_by=founded_by,
        )
        session.add(comm)
        await session.commit()
        return comm.id


async def get_community(community_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Community).where(Community.id == community_id)
        )
        comm = result.scalar_one_or_none()
        if not comm:
            return None
        members_result = await session.execute(
            select(CommunityMember).where(CommunityMember.community_id == community_id)
            .where(CommunityMember.status == "active")
        )
        members = members_result.scalars().all()
        return {
            "id": comm.id,
            "name": comm.name,
            "description": comm.description,
            "community_type": comm.community_type,
            "purpose": comm.purpose,
            "industry": comm.industry,
            "member_count": comm.member_count,
            "knowledge_pool_size": comm.knowledge_pool_size,
            "reputation": comm.reputation,
            "status": comm.status,
            "founded_by": comm.founded_by,
            "members": [
                {
                    "id": m.id,
                    "member_id": m.member_id,
                    "member_type": m.member_type,
                    "role": m.role,
                    "contribution_score": m.contribution_score,
                    "knowledge_shared": m.knowledge_shared,
                }
                for m in members
            ],
            "created_at": comm.created_at.isoformat() if comm.created_at else None,
        }


async def list_communities(community_type: str | None = None, industry: str | None = None,
                           limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Community).where(Community.status == "active")
        if community_type:
            stmt = stmt.where(Community.community_type == community_type)
        if industry:
            stmt = stmt.where(Community.industry == industry)
        stmt = stmt.order_by(Community.member_count.desc()).limit(limit)
        result = await session.execute(stmt)
        comms = result.scalars().all()
        return [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "community_type": c.community_type,
                "purpose": c.purpose,
                "industry": c.industry,
                "member_count": c.member_count,
                "reputation": c.reputation,
                "status": c.status,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in comms
        ]


async def join_community(community_id: str, member_id: str, member_type: str = "agent",
                         role: str = "member") -> str:
    async with async_session_factory() as session:
        existing = await session.execute(
            select(CommunityMember).where(
                and_(CommunityMember.community_id == community_id,
                     CommunityMember.member_id == member_id)
            )
        )
        if existing.scalar_one_or_none():
            return ""
        cm = CommunityMember(
            community_id=community_id, member_id=member_id,
            member_type=member_type, role=role,
        )
        session.add(cm)
        comm_result = await session.execute(
            select(Community).where(Community.id == community_id)
        )
        comm = comm_result.scalar_one_or_none()
        if comm:
            comm.member_count = (comm.member_count or 0) + 1
        await session.commit()
        return cm.id


async def get_community_members(community_id: str) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(CommunityMember).where(
                and_(CommunityMember.community_id == community_id,
                     CommunityMember.status == "active")
            )
        )
        members = result.scalars().all()
        return [
            {
                "id": m.id,
                "member_id": m.member_id,
                "member_type": m.member_type,
                "role": m.role,
                "contribution_score": m.contribution_score,
                "knowledge_shared": m.knowledge_shared,
                "joined_at": m.joined_at.isoformat() if m.joined_at else None,
            }
            for m in members
        ]


async def get_communication_stats() -> dict:
    async with async_session_factory() as session:
        msg_count = await session.execute(select(func.count(Message.id)))
        conv_count = await session.execute(select(func.count(Conversation.id)))
        conn_count = await session.execute(select(func.count(SocialConnection.id)))
        comm_count = await session.execute(select(func.count(Community.id)))
        ks_count = await session.execute(select(func.count(KnowledgeShare.id)))
        return {
            "total_messages": msg_count.scalar() or 0,
            "total_conversations": conv_count.scalar() or 0,
            "total_social_connections": conn_count.scalar() or 0,
            "total_communities": comm_count.scalar() or 0,
            "total_knowledge_shares": ks_count.scalar() or 0,
        }


async def mark_message_read(message_id: str) -> None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(Message).where(Message.id == message_id)
        )
        msg = result.scalar_one_or_none()
        if msg:
            msg.status = "read"
            msg.read_at = datetime.now(timezone.utc)
            await session.commit()
