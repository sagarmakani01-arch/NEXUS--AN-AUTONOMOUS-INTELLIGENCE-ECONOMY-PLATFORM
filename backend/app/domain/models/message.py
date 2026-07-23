import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String(36), nullable=False, index=True)
    sender_type = Column(String(20), nullable=False, default="agent")
    receiver_id = Column(String(36), nullable=False, index=True)
    receiver_type = Column(String(20), nullable=False, default="agent")
    conversation_id = Column(String(36), index=True, nullable=True)
    message_type = Column(String(30), nullable=False, default="private")
    content = Column(Text, nullable=False)
    priority = Column(String(20), default="normal")
    status = Column(String(20), default="sent")
    reply_to_id = Column(String(36), nullable=True)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True), nullable=True)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=True)
    topic = Column(String(100), nullable=True)
    conversation_type = Column(String(30), nullable=False, default="private")
    summary = Column(Text, nullable=True)
    decisions = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    status = Column(String(20), default="active")
    message_count = Column(Integer, default=0)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)


class ConversationParticipant(Base):
    __tablename__ = "conversation_participants"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), nullable=False, index=True)
    participant_id = Column(String(36), nullable=False, index=True)
    participant_type = Column(String(20), nullable=False, default="agent")
    role = Column(String(30), default="member")
    last_read_at = Column(DateTime(timezone=True), nullable=True)
    notification_count = Column(Integer, default=0)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KnowledgeShare(Base):
    __tablename__ = "knowledge_shares"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), nullable=False, index=True)
    owner_type = Column(String(20), nullable=False, default="agent")
    knowledge_type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    visibility = Column(String(20), default="private")
    tags = Column(Text, default="[]")
    access_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    metadata_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
