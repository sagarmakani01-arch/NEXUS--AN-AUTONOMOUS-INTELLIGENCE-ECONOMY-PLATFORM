import logging
import random
from app.culture import persistence as db

logger = logging.getLogger("nexus.culture.communities")

COMMUNITY_TYPES = ["professional", "research_interest", "shared_goal", "location", "historical"]


async def initialize_communities(civ_id: str) -> list[dict]:
    existing = await db.list_communities(civ_id)
    if existing:
        return existing
    defaults = [
        ("Pioneers Circle", "professional", "Founding agents and early contributors"),
        ("Research Collective", "research_interest", "Active researchers and scientists"),
        ("Trade Network", "shared_goal", "Commerce and resource exchange"),
    ]
    created = []
    for name, ctype, desc in defaults:
        cid = await db.create_community(
            civilization_id=civ_id,
            name=name,
            description=desc,
            community_type=ctype,
            member_count=random.randint(3, 10),
            growth_rate=0.0,
        )
        created.append({"id": cid, "name": name})
    logger.info("Initialized %d communities for civ %s", len(created), civ_id)
    return created


async def create_community(civ_id: str, name: str, community_type: str | None = None,
                           description: str | None = None) -> dict:
    if community_type not in COMMUNITY_TYPES:
        community_type = random.choice(COMMUNITY_TYPES)
    cid = await db.create_community(
        civilization_id=civ_id,
        name=name,
        description=description,
        community_type=community_type,
        member_count=1,
        growth_rate=0.0,
    )
    await db.create_cultural_timeline(
        civilization_id=civ_id,
        change_type="community_created",
        description=f"Community '{name}' created",
        cause="agent_initiative",
        impact_score=15.0,
    )
    communities = await db.list_communities(civ_id)
    return next((c for c in communities if c["id"] == cid), {})


async def join_community(community_id: str, entity_id: str, entity_type: str = "agent",
                         role: str = "member") -> dict | None:
    community = await db.get_community(community_id)
    if not community:
        return None
    mid = await db.create_community_membership(
        community_id=community_id,
        entity_id=entity_id,
        entity_type=entity_type,
        role=role,
    )
    new_count = community["member_count"] + 1
    growth = ((new_count - community["member_count"]) / max(1, community["member_count"])) * 100
    await db.update_community(
        community_id,
        member_count=new_count,
        growth_rate=round(growth, 2),
    )
    return {"membership_id": mid, "community": community["name"]}


async def leave_community(community_id: str, entity_id: str) -> dict | None:
    community = await db.get_community(community_id)
    if not community:
        return None
    new_count = max(0, community["member_count"] - 1)
    await db.update_community(
        community_id,
        member_count=new_count,
        growth_rate=round(-100.0 / max(1, community["member_count"]), 2),
    )
    return {"community": community["name"], "entity_id": entity_id}


async def grow_communities(civ_id: str) -> dict:
    communities = await db.list_communities(civ_id)
    grew = 0
    for c in communities:
        if c["member_count"] > 0 and random.random() > 0.7:
            new_count = c["member_count"] + random.randint(0, 2)
            growth = ((new_count - c["member_count"]) / max(1, c["member_count"])) * 100
            await db.update_community(c["id"], member_count=new_count, growth_rate=round(growth, 2))
            grew += 1
    return {"communities_grew": grew}


def get_state() -> dict:
    return {"community_types": COMMUNITY_TYPES, "initialized": True}
