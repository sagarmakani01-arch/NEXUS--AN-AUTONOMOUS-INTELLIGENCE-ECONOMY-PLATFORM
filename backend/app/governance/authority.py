import logging

from app.governance import persistence as gov_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.authority")

AUTHORITY_LEVELS = ["individual", "company", "organization", "government"]

LEVEL_PERMISSIONS = {
    "individual": [
        "create_contracts", "join_communities", "vote_in_community",
        "share_knowledge", "engage_in_conflict",
    ],
    "company": [
        "create_contracts", "hire_employees", "create_internal_policies",
        "manage_resources", "compete_in_market", "form_partnerships",
        "access_loans", "make_investments",
    ],
    "organization": [
        "create_contracts", "hire_employees", "create_policies",
        "manage_resources", "compete_in_market", "form_partnerships",
        "create_regulations", "organize_communities", "manage_budget",
    ],
    "government": [
        "create_laws", "create_policies", "create_taxes", "create_regulations",
        "enforce_laws", "resolve_conflicts", "manage公共资源",
        "collect_taxes", "allocate_budget", "call_votes",
        "declare_emergency", "amend_constitution",
    ],
}


class AuthoritySystem:
    def __init__(self):
        self.stats = {
            "entities_created": 0,
            "authority_upgrades": 0,
        }

    async def create_entity(self, name: str, entity_type: str, description: str | None = None,
                            authority_level: str = "individual",
                            founder_id: str | None = None) -> dict:
        if authority_level not in AUTHORITY_LEVELS:
            authority_level = "individual"

        entity_id = await gov_db.create_governance_entity(
            name=name, entity_type=entity_type,
            description=description, authority_level=authority_level,
            founder_id=founder_id,
        )
        self.stats["entities_created"] += 1

        await dispatch(Event(EventType.AUTHORITY_CREATED, {
            "entity_id": entity_id, "name": name,
            "entity_type": entity_type, "authority_level": authority_level,
        }))

        return {
            "entity_id": entity_id,
            "name": name,
            "authority_level": authority_level,
            "permissions": LEVEL_PERMISSIONS.get(authority_level, []),
            "status": "created",
        }

    async def get_entity(self, entity_id: str) -> dict | None:
        return await gov_db.get_governance_entity(entity_id)

    async def list_entities(self, entity_type: str | None = None,
                            authority_level: str | None = None) -> list[dict]:
        return await gov_db.list_governance_entities(entity_type, authority_level)

    def check_permission(self, authority_level: str, permission: str) -> bool:
        perms = LEVEL_PERMISSIONS.get(authority_level, [])
        return permission in perms

    def get_permissions(self, authority_level: str) -> list[str]:
        return LEVEL_PERMISSIONS.get(authority_level, [])

    async def upgrade_authority(self, entity_id: str, new_level: str) -> dict:
        entity = await gov_db.get_governance_entity(entity_id)
        if not entity:
            return {"success": False, "error": "Entity not found"}
        if new_level not in AUTHORITY_LEVELS:
            return {"success": False, "error": "Invalid authority level"}

        current_idx = AUTHORITY_LEVELS.index(entity["authority_level"])
        new_idx = AUTHORITY_LEVELS.index(new_level)
        if new_idx <= current_idx:
            return {"success": False, "error": "Can only upgrade to higher level"}

        await gov_db.update_governance_entity(entity_id, authority_level=new_level)
        self.stats["authority_upgrades"] += 1

        return {
            "success": True,
            "previous_level": entity["authority_level"],
            "new_level": new_level,
            "new_permissions": self.get_permissions(new_level),
        }

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "authority_levels": AUTHORITY_LEVELS,
            "level_permissions": {k: len(v) for k, v in LEVEL_PERMISSIONS.items()},
        }


authority_system = AuthoritySystem()
