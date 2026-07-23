from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/communication", tags=["Communication & Social"])


class SendMessageRequest(BaseModel):
    sender_id: str
    sender_type: str = "agent"
    receiver_id: str
    receiver_type: str = "agent"
    content: str
    message_type: str = "private"
    priority: str = "normal"


class CreateConversationRequest(BaseModel):
    title: str | None = None
    topic: str | None = None
    conversation_type: str = "private"
    participants: list[dict] | None = None


class CreateConnectionRequest(BaseModel):
    entity_a_id: str
    entity_a_type: str = "agent"
    entity_b_id: str
    entity_b_type: str = "agent"
    relationship_type: str = "colleague"
    trust_level: float = 50.0


class ShareKnowledgeRequest(BaseModel):
    owner_id: str
    owner_type: str = "agent"
    knowledge_type: str
    title: str
    content: str
    visibility: str = "private"
    tags: list[str] | None = None


class CreateCommunityRequest(BaseModel):
    name: str
    description: str | None = None
    community_type: str = "open"
    purpose: str | None = None
    industry: str | None = None
    founded_by: str | None = None


class JoinCommunityRequest(BaseModel):
    community_id: str
    member_id: str
    member_type: str = "agent"
    role: str = "member"


@router.post("/messages/send")
async def send_message(req: SendMessageRequest):
    from app.communication.messaging import messaging_system
    result = await messaging_system.send_message(
        sender_id=req.sender_id, sender_type=req.sender_type,
        receiver_id=req.receiver_id, receiver_type=req.receiver_type,
        content=req.content, message_type=req.message_type,
        priority=req.priority,
    )
    return result


@router.get("/messages/inbox/{entity_id}")
async def get_inbox(entity_id: str):
    from app.communication.messaging import messaging_system
    return await messaging_system.get_entity_inbox(entity_id)


@router.get("/messages/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    from app.communication.messaging import messaging_system
    conv = await messaging_system.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get("/messages/search")
async def search_messages(q: str, entity_id: str | None = None):
    from app.communication.messaging import messaging_system
    return await messaging_system.search_messages(q, entity_id)


@router.post("/conversations/create")
async def create_conversation(req: CreateConversationRequest):
    from app.communication import persistence as comm_db
    conv_id = await comm_db.create_conversation(
        title=req.title, topic=req.topic,
        conversation_type=req.conversation_type,
        participants=req.participants,
    )
    return {"conversation_id": conv_id, "status": "created"}


@router.get("/conversations/{entity_id}")
async def get_entity_conversations(entity_id: str):
    from app.communication import persistence as comm_db
    return await comm_db.get_entity_conversations(entity_id)


@router.post("/social/connections/create")
async def create_connection(req: CreateConnectionRequest):
    from app.communication.social_graph import social_graph
    return await social_graph.create_connection(
        entity_a_id=req.entity_a_id, entity_a_type=req.entity_a_type,
        entity_b_id=req.entity_b_id, entity_b_type=req.entity_b_type,
        relationship_type=req.relationship_type, trust_level=req.trust_level,
    )


@router.get("/social/network/{entity_id}")
async def get_social_network(entity_id: str):
    from app.communication.social_graph import social_graph
    return await social_graph.get_network(entity_id)


@router.get("/social/trust/{entity_a_id}/{entity_b_id}")
async def get_trust_assessment(entity_a_id: str, entity_b_id: str):
    from app.communication.trust import trust_system
    return await trust_system.get_trust_assessment(entity_a_id, entity_b_id)


@router.get("/social/trust/overview/{entity_id}")
async def get_trust_overview(entity_id: str):
    from app.communication.trust import trust_system
    return await trust_system.get_entity_trust_overview(entity_id)


@router.get("/social/trust/history/{entity_a_id}/{entity_b_id}")
async def get_trust_history(entity_a_id: str, entity_b_id: str):
    from app.communication import persistence as comm_db
    return await comm_db.get_trust_history(entity_a_id, entity_b_id)


@router.get("/social/influence/{entity_id}")
async def get_influence_score(entity_id: str):
    from app.communication.social_graph import social_graph
    score = await social_graph.calculate_influence_score(entity_id)
    return {"entity_id": entity_id, "influence_score": score}


@router.get("/social/suggestions/{entity_id}")
async def get_connection_suggestions(entity_id: str):
    from app.communication.social_graph import social_graph
    return await social_graph.suggest_connections(entity_id)


@router.post("/knowledge/share")
async def share_knowledge(req: ShareKnowledgeRequest):
    from app.communication.knowledge import knowledge_exchange
    return await knowledge_exchange.share_knowledge(
        owner_id=req.owner_id, owner_type=req.owner_type,
        knowledge_type=req.knowledge_type, title=req.title,
        content=req.content, visibility=req.visibility, tags=req.tags,
    )


@router.get("/knowledge/search")
async def search_knowledge(q: str | None = None, knowledge_type: str | None = None,
                           visibility: str | None = None):
    from app.communication.knowledge import knowledge_exchange
    return await knowledge_exchange.search_knowledge(q, knowledge_type, visibility)


@router.get("/knowledge/entity/{entity_id}")
async def get_entity_knowledge(entity_id: str):
    from app.communication.knowledge import knowledge_exchange
    return await knowledge_exchange.get_entity_knowledge(entity_id)


@router.get("/knowledge/{knowledge_id}")
async def access_knowledge(knowledge_id: str):
    from app.communication.knowledge import knowledge_exchange
    result = await knowledge_exchange.access_knowledge(knowledge_id)
    if not result:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return result


@router.post("/communities/create")
async def create_community(req: CreateCommunityRequest):
    from app.communication.communities import communities_system
    return await communities_system.create_community(
        name=req.name, description=req.description,
        community_type=req.community_type, purpose=req.purpose,
        industry=req.industry, founded_by=req.founded_by,
    )


@router.get("/communities")
async def list_communities(community_type: str | None = None, industry: str | None = None):
    from app.communication.communities import communities_system
    return await communities_system.list_communities(community_type, industry)


@router.get("/communities/{community_id}")
async def get_community(community_id: str):
    from app.communication.communities import communities_system
    comm = await communities_system.get_community(community_id)
    if not comm:
        raise HTTPException(status_code=404, detail="Community not found")
    return comm


@router.post("/communities/join")
async def join_community(req: JoinCommunityRequest):
    from app.communication.communities import communities_system
    return await communities_system.join_community(
        community_id=req.community_id, member_id=req.member_id,
        member_type=req.member_type, role=req.role,
    )


@router.get("/communities/{community_id}/members")
async def get_community_members(community_id: str):
    from app.communication.communities import communities_system
    return await communities_system.get_community_members(community_id)


@router.get("/communities/entity/{entity_id}")
async def get_entity_communities(entity_id: str):
    from app.communication.communities import communities_system
    return await communities_system.get_entity_communities(entity_id)


@router.get("/intelligence/{entity_id}")
async def get_social_intelligence(entity_id: str):
    from app.communication.intelligence import communication_intelligence
    return await communication_intelligence.get_agent_social_intelligence(entity_id)


@router.get("/intelligence/context/{sender_id}/{receiver_id}")
async def get_communication_context(sender_id: str, receiver_id: str):
    from app.communication.intelligence import communication_intelligence
    return await communication_intelligence.analyze_communication_context(sender_id, receiver_id)


@router.get("/agent/{agent_id}")
async def get_agent_communication_state(agent_id: str):
    from app.communication.engine import communication_engine
    return await communication_engine.get_agent_communication_state(agent_id)


@router.get("/engine/state")
async def get_engine_state():
    from app.communication.engine import communication_engine
    return communication_engine.get_state()


@router.get("/engine/stats")
async def get_engine_stats():
    from app.communication import persistence as comm_db
    return await comm_db.get_communication_stats()
