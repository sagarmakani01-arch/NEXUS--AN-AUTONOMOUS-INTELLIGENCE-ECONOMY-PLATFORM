import logging

from app.communication import persistence as comm_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.communication.communities")

COMMUNITY_TYPES = ["open", "closed", "professional", "interest", "industry"]
INDUSTRIES = [
    "technology", "finance", "healthcare", "education", "research",
    "manufacturing", "energy", "retail", "media", "consulting",
]


class CommunitiesSystem:
    def __init__(self):
        self.stats = {
            "communities_created": 0,
            "members_joined": 0,
        }

    async def create_community(self, name: str, description: str | None,
                               community_type: str = "open", purpose: str | None = None,
                               industry: str | None = None, founded_by: str | None = None) -> dict:
        if community_type not in COMMUNITY_TYPES:
            community_type = "open"

        comm_id = await comm_db.create_community(
            name=name,
            description=description,
            community_type=community_type,
            purpose=purpose,
            industry=industry,
            founded_by=founded_by,
        )
        self.stats["communities_created"] += 1

        if founded_by:
            await comm_db.join_community(comm_id, founded_by, "agent", "founder")
            self.stats["members_joined"] += 1

        await dispatch(Event(EventType.COMMUNITY_FORMED, {
            "community_id": comm_id,
            "name": name,
            "community_type": community_type,
            "founded_by": founded_by,
        }))

        return {
            "community_id": comm_id,
            "name": name,
            "status": "created",
        }

    async def get_community(self, community_id: str) -> dict | None:
        return await comm_db.get_community(community_id)

    async def list_communities(self, community_type: str | None = None,
                               industry: str | None = None) -> list[dict]:
        return await comm_db.list_communities(community_type, industry)

    async def join_community(self, community_id: str, member_id: str,
                             member_type: str = "agent", role: str = "member") -> dict:
        member_record_id = await comm_db.join_community(community_id, member_id, member_type, role)
        if not member_record_id:
            return {"status": "already_member"}
        self.stats["members_joined"] += 1
        return {
            "community_id": community_id,
            "member_id": member_id,
            "role": role,
            "status": "joined",
        }

    async def get_community_members(self, community_id: str) -> list[dict]:
        return await comm_db.get_community_members(community_id)

    async def get_entity_communities(self, entity_id: str) -> dict:
        all_communities = await comm_db.list_communities()
        member_communities = []
        for comm in all_communities:
            members = await comm_db.get_community_members(comm["id"])
            for m in members:
                if m["member_id"] == entity_id:
                    member_communities.append(comm)
                    break
        return {
            "entity_id": entity_id,
            "member_communities": member_communities,
            "total_communities": len(member_communities),
        }

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "community_types": COMMUNITY_TYPES,
            "industries": INDUSTRIES,
        }


communities_system = CommunitiesSystem()
