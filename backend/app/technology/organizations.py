import logging
import random
from app.technology import persistence as db

logger = logging.getLogger("nexus.technology.organizations")

ORG_TYPES = ["research_university", "technology_company", "government_lab", "independent_researcher"]


async def initialize_organizations(civ_id: str) -> list[dict]:
    existing = await db.list_scientific_organizations(civ_id)
    if existing:
        return existing
    defaults = [
        ("NEXUS University", "research_university", "Central research university"),
        ("TechCorp Labs", "technology_company", "Private technology R&D"),
        ("Gov Science Institute", "government_lab", "Government research facility"),
    ]
    created = []
    for name, otype, desc in defaults:
        oid = await db.create_scientific_organization(
            civilization_id=civ_id, name=name, org_type=otype,
            description=desc,
            funding_level=random.uniform(40.0, 80.0),
            reputation=random.uniform(40.0, 70.0),
            specialization=str(["AI", "Robotics"]),
        )
        created.append({"id": oid, "name": name})
    return created


async def create_organization(civ_id: str, name: str, org_type: str | None = None,
                              description: str | None = None) -> dict:
    if org_type not in ORG_TYPES:
        org_type = random.choice(ORG_TYPES)
    oid = await db.create_scientific_organization(
        civilization_id=civ_id, name=name, org_type=org_type,
        description=description,
        funding_level=random.uniform(30.0, 60.0),
        reputation=random.uniform(30.0, 50.0),
    )
    orgs = await db.list_scientific_organizations(civ_id)
    return next((o for o in orgs if o["id"] == oid), {})


def get_state() -> dict:
    return {"org_types": ORG_TYPES, "initialized": True}
