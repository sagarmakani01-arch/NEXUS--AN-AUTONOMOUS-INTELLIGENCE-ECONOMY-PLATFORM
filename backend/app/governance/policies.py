import logging
from datetime import datetime, timezone, timedelta

from app.governance import persistence as gov_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.policies")

POLICY_TYPES = [
    "economic", "resource", "employment", "research",
    "security", "social", "environmental", "trade",
]


class PolicyEngine:
    def __init__(self):
        self.stats = {
            "policies_created": 0,
            "policies_expired": 0,
        }

    async def create_policy(self, name: str, description: str | None, policy_type: str,
                            creator_id: str, target: str | None = None,
                            rules: dict | None = None, expected_outcome: str | None = None,
                            duration_days: int = 30, priority: str = "medium") -> dict:
        if policy_type not in POLICY_TYPES:
            policy_type = "social"

        policy_id = await gov_db.create_policy(
            name=name, description=description, policy_type=policy_type,
            creator_id=creator_id, target=target, rules=rules,
            expected_outcome=expected_outcome, duration_days=duration_days,
            priority=priority,
        )
        self.stats["policies_created"] += 1

        await gov_db.record_governance(
            record_type="policy_created", title=f"New Policy: {name}",
            actor_id=creator_id, description=description,
            related_ids=[policy_id],
            impact={"policy_type": policy_type, "duration_days": duration_days},
        )

        await dispatch(Event(EventType.POLICY_CHANGED, {
            "policy_id": policy_id, "name": name,
            "policy_type": policy_type, "creator_id": creator_id,
            "duration_days": duration_days,
        }))

        return {
            "policy_id": policy_id,
            "name": name,
            "policy_type": policy_type,
            "duration_days": duration_days,
            "status": "active",
        }

    async def get_policy(self, policy_id: str) -> dict | None:
        return await gov_db.get_policy(policy_id)

    async def list_policies(self, policy_type: str | None = None) -> list[dict]:
        return await gov_db.list_policies(policy_type)

    async def update_compliance(self, policy_id: str, compliant: bool) -> dict:
        policy = await gov_db.get_policy(policy_id)
        if not policy:
            return {"success": False, "error": "Policy not found"}
        current = policy.get("compliance_rate", 100.0)
        if compliant:
            new_rate = min(100.0, current + 5.0)
        else:
            new_rate = max(0.0, current - 10.0)
        await gov_db.update_policy(policy_id, compliance_rate=new_rate)
        return {"policy_id": policy_id, "compliance_rate": new_rate}

    async def check_expired_policies(self) -> int:
        policies = await gov_db.list_policies()
        expired_count = 0
        for policy in policies:
            created = policy.get("created_at")
            if created:
                from datetime import datetime as dt
                try:
                    created_dt = dt.fromisoformat(created.replace("Z", "+00:00"))
                    duration = policy.get("duration_days", 30)
                    if dt.now(timezone.utc) > created_dt + timedelta(days=duration):
                        await gov_db.update_policy(policy["id"], status="expired")
                        expired_count += 1
                except Exception:
                    pass
        self.stats["policies_expired"] += expired_count
        return expired_count

    async def get_policy_stats(self) -> dict:
        policies = await gov_db.list_policies()
        types = {}
        for p in policies:
            pt = p.get("policy_type", "general")
            if pt not in types:
                types[pt] = 0
            types[pt] += 1
        return {
            "total_policies": len(policies),
            "by_type": types,
            "stats": self.stats.copy(),
        }

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "policy_types": POLICY_TYPES,
        }


policy_engine = PolicyEngine()
