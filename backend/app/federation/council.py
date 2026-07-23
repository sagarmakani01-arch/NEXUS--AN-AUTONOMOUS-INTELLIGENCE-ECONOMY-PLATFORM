import json
import logging

from app.federation import persistence as db

logger = logging.getLogger("nexus.federation.council")


class FederationCouncilManager:
    def __init__(self):
        self.stats = {"councils_created": 0, "memberships": 0}

    async def create_council(self, name: str, founding_civ_id: str,
                             description: str | None = None) -> dict:
        council_id = await db.create_federation_council(
            name=name, description=description,
            founding_civilization_id=founding_civ_id,
            member_civilization_ids=json.dumps([founding_civ_id]),
        )
        self.stats["councils_created"] += 1
        return {"council_id": council_id, "name": name}

    async def join_council(self, council_id: str, civ_id: str) -> dict:
        council = await db.get_federation_council(council_id)
        if not council:
            return {"success": False, "error": "Council not found"}
        members = council.get("member_civilization_ids", [])
        if civ_id in members:
            return {"success": False, "error": "Already a member"}
        members.append(civ_id)
        await db.update_federation_council(council_id, member_civilization_ids=json.dumps(members))
        self.stats["memberships"] += 1
        return {"success": True, "member_count": len(members)}

    async def get_council(self, council_id: str) -> dict | None:
        return await db.get_federation_council(council_id)

    async def list_councils(self) -> list[dict]:
        return await db.list_federation_councils()

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


federation_council_manager = FederationCouncilManager()
