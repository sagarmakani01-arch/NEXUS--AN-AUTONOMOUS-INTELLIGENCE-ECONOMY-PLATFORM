import logging
import random
from datetime import datetime, timezone

from app.governance import persistence as gov_db
from app.communication.trust import trust_system
from app.resources.persistence import get_wallet, update_balance, create_transaction
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.conflict")

CONFLICT_TYPES = [
    "contract_disagreement", "resource_dispute", "partnership_failure",
    "intellectual_property", "labor_dispute", "financial_dispute",
    "reputation_damage", "policy_violation",
]


class ConflictResolution:
    def __init__(self):
        self.stats = {
            "conflicts_created": 0,
            "conflicts_resolved": 0,
            "negotiations_successful": 0,
            "arbitrations_completed": 0,
        }

    async def create_conflict(self, plaintiff_id: str, plaintiff_type: str,
                              defendant_id: str, defendant_type: str,
                              conflict_type: str, description: str | None = None,
                              resolution_method: str = "arbitration") -> dict:
        if conflict_type not in CONFLICT_TYPES:
            conflict_type = "contract_disagreement"

        conflict_id = await gov_db.create_conflict(
            plaintiff_id=plaintiff_id, plaintiff_type=plaintiff_type,
            defendant_id=defendant_id, defendant_type=defendant_type,
            conflict_type=conflict_type, description=description,
            resolution_method=resolution_method,
        )
        self.stats["conflicts_created"] += 1

        await trust_system.process_interaction(
            plaintiff_id, plaintiff_type, defendant_id, defendant_type, "conflict",
        )

        await dispatch(Event(EventType.CONFLICT_STARTED, {
            "conflict_id": conflict_id, "plaintiff_id": plaintiff_id,
            "defendant_id": defendant_id, "conflict_type": conflict_type,
        }))

        return {
            "conflict_id": conflict_id,
            "plaintiff_id": plaintiff_id,
            "defendant_id": defendant_id,
            "conflict_type": conflict_type,
            "resolution_method": resolution_method,
            "status": "open",
        }

    async def resolve_negotiation(self, conflict_id: str) -> dict:
        conflict = await gov_db.get_conflict(conflict_id)
        if not conflict or conflict["status"] != "open":
            return {"success": False, "error": "Conflict not found or not open"}

        success_chance = random.uniform(0.3, 0.7)
        if random.random() < success_chance:
            resolution = "Mutual agreement reached through negotiation"
            penalty = 0.0
            await gov_db.update_conflict(
                conflict_id, status="resolved", resolution=resolution,
                resolved_at=datetime.now(timezone.utc),
            )
            self.stats["conflicts_resolved"] += 1
            self.stats["negotiations_successful"] += 1
            await trust_system.process_interaction(
                conflict["plaintiff_id"], conflict["plaintiff_type"],
                conflict["defendant_id"], conflict["defendant_type"],
                "positive_outcome",
            )
            return {
                "success": True, "method": "negotiation",
                "resolution": resolution, "penalty": 0.0,
            }
        else:
            resolution = "Negotiation failed, case escalated to arbitration"
            await gov_db.update_conflict(
                conflict_id, resolution_method="arbitration",
                resolution=resolution,
            )
            return {
                "success": False, "method": "negotiation",
                "resolution": resolution, "escalated": True,
            }

    async def resolve_arbitration(self, conflict_id: str) -> dict:
        conflict = await gov_db.get_conflict(conflict_id)
        if not conflict or conflict["status"] != "open":
            return {"success": False, "error": "Conflict not found or not open"}

        plaintiff_wins = random.random() > 0.4
        if plaintiff_wins:
            penalty = random.uniform(10, 100)
            ruling = f"Arbitration ruling in favor of plaintiff. Defendant pays {penalty:.0f} NXC."
            winner_id = conflict["plaintiff_id"]
            loser_id = conflict["defendant_id"]
        else:
            penalty = random.uniform(10, 50)
            ruling = f"Arbitration ruling in favor of defendant. Plaintiff pays {penalty:.0f} NXC in damages."
            winner_id = conflict["defendant_id"]
            loser_id = conflict["plaintiff_id"]

        wallet = await get_wallet(loser_id)
        if wallet and wallet.get("balance", 0) >= penalty:
            await update_balance(loser_id, -penalty)
            await update_balance(winner_id, penalty)
            await create_transaction(
                from_wallet_id=loser_id, to_wallet_id=winner_id,
                amount=penalty, transaction_type="arbitration_penalty",
                notes=f"Arbitration penalty for conflict {conflict_id}",
            )

        await gov_db.update_conflict(
            conflict_id, status="resolved", ruling=ruling,
            resolution="Arbitration completed", penalty_amount=penalty,
            resolved_at=datetime.now(timezone.utc),
        )
        self.stats["conflicts_resolved"] += 1
        self.stats["arbitrations_completed"] += 1

        await dispatch(Event(EventType.CONFLICT_RESOLVED, {
            "conflict_id": conflict_id, "winner_id": winner_id,
            "loser_id": loser_id, "penalty": penalty,
        }))

        return {
            "success": True, "method": "arbitration",
            "ruling": ruling, "penalty": penalty,
            "winner_id": winner_id, "loser_id": loser_id,
        }

    async def get_open_conflicts(self) -> list[dict]:
        return await gov_db.list_conflicts(status="open")

    async def get_conflict_history(self, party_id: str | None = None) -> list[dict]:
        return await gov_db.list_conflicts(party_id=party_id)

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "conflict_types": CONFLICT_TYPES,
        }


conflict_resolution = ConflictResolution()
