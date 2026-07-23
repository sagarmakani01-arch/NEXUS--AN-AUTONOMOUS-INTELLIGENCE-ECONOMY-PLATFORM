import json
import logging
import random

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.organizations")

ORG_TYPES = {
    "university": {"reputation_base": 60, "budget_range": (100, 500), "research_areas": 5,
                   "description": "Academic research institution focused on fundamental knowledge"},
    "corporate_lab": {"reputation_base": 50, "budget_range": (200, 1000), "research_areas": 3,
                      "description": "Industry R&D facility focused on commercial applications"},
    "government_institute": {"reputation_base": 55, "budget_range": (150, 800), "research_areas": 4,
                             "description": "Government-funded research body serving public interest"},
    "independent": {"reputation_base": 40, "budget_range": (50, 200), "research_areas": 2,
                    "description": "Independent research collective or individual researchers"},
}

DEFAULT_RESEARCH_AREAS = [
    "Artificial Intelligence", "Quantum Computing", "Biotechnology",
    "Materials Science", "Neuroscience", "Climate Science",
    "Economics", "Sociology", "Physics", "Chemistry",
    "Computer Science", "Mathematics", "Medicine", "Ecology",
]


class OrganizationManager:
    def __init__(self):
        self.stats = {
            "organizations_created": 0,
            "scientists_hired": 0,
            "budgets_allocated": 0,
        }

    async def create_organization(self, name: str, org_type: str,
                                  founder_agent_id: str | None = None,
                                  research_areas: list[str] | None = None,
                                  initial_budget: float = 0) -> dict:
        config = ORG_TYPES.get(org_type, ORG_TYPES["university"])
        if not research_areas:
            research_areas = random.sample(DEFAULT_RESEARCH_AREAS, config["research_areas"])

        budget = initial_budget or random.uniform(*config["budget_range"])
        org_id = await db.create_organization(
            name=name, org_type=org_type, founder_agent_id=founder_agent_id,
            research_budget=budget, reputation=config["reputation_base"],
            research_areas=json.dumps(research_areas),
        )
        self.stats["organizations_created"] += 1

        await dispatch(Event(EventType.RESEARCH_STARTED, {
            "organization_id": org_id, "name": name, "type": org_type,
        }))
        return {"organization_id": org_id, "name": name, "type": org_type, "budget": budget}

    async def add_scientist(self, org_id: str, agent_id: str) -> dict:
        org = await db.get_organization(org_id)
        if not org:
            return {"success": False, "error": "Organization not found"}
        scientists = org.get("scientist_agent_ids", [])
        if agent_id in scientists:
            return {"success": False, "error": "Already a member"}
        scientists.append(agent_id)
        await db.update_organization(org_id, scientist_agent_ids=json.dumps(scientists))
        self.stats["scientists_hired"] += 1
        return {"success": True, "scientist_count": len(scientists)}

    async def allocate_budget(self, org_id: str, amount: float) -> dict:
        org = await db.get_organization(org_id)
        if not org:
            return {"success": False, "error": "Organization not found"}
        new_budget = org["research_budget"] + amount
        await db.update_organization(org_id, research_budget=new_budget)
        self.stats["budgets_allocated"] += 1
        return {"success": True, "new_budget": new_budget}

    async def get_organization(self, org_id: str) -> dict | None:
        return await db.get_organization(org_id)

    async def list_organizations(self, org_type: str | None = None) -> list[dict]:
        return await db.list_organizations(org_type)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


organization_manager = OrganizationManager()
