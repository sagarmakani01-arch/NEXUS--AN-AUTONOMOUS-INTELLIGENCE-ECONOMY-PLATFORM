import logging

from app.governance import persistence as gov_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.regulation")

REGULATION_TYPES = [
    "licensing", "safety", "environmental", "financial",
    "labor", "data_protection", "fair_trade", "quality",
]


class RegulationSystem:
    def __init__(self):
        self.violations: dict[str, int] = {}
        self.stats = {
            "regulations_created": 0,
            "violations_detected": 0,
            "penalties_applied": 0,
        }

    async def create_regulation(self, name: str, description: str | None,
                                regulation_type: str, authority_id: str,
                                target_sector: str | None = None,
                                requirements: dict | None = None,
                                max_violations: int = 3,
                                penalty_description: str | None = None) -> dict:
        if regulation_type not in REGULATION_TYPES:
            regulation_type = "quality"

        reg_id = await gov_db.create_regulation(
            name=name, description=description,
            regulation_type=regulation_type, authority_id=authority_id,
            target_sector=target_sector, requirements=requirements,
            max_violations=max_violations,
            penalty_description=penalty_description,
        )
        self.stats["regulations_created"] += 1

        await gov_db.record_governance(
            record_type="regulation_created", title=f"New Regulation: {name}",
            actor_id=authority_id, description=description,
            related_ids=[reg_id],
            impact={"regulation_type": regulation_type, "sector": target_sector},
        )

        return {
            "regulation_id": reg_id,
            "name": name,
            "regulation_type": regulation_type,
            "status": "active",
        }

    async def report_violation(self, entity_id: str, regulation_id: str) -> dict:
        key = f"{entity_id}:{regulation_id}"
        self.violations[key] = self.violations.get(key, 0) + 1
        self.stats["violations_detected"] += 1

        regs = await gov_db.list_regulations()
        max_violations = 3
        for reg in regs:
            if reg["id"] == regulation_id:
                max_violations = reg.get("max_violations", 3)
                break

        penalty_applied = False
        if self.violations[key] >= max_violations:
            penalty_applied = True
            self.stats["penalties_applied"] += 1
            await gov_db.record_governance(
                record_type="violation_penalty",
                title=f"Penalty applied to {entity_id}",
                actor_id="government",
                entity_id=entity_id,
                description=f"Exceeded max violations ({max_violations}) for regulation",
                related_ids=[regulation_id],
                impact={"violation_count": self.violations[key]},
            )

        return {
            "entity_id": entity_id,
            "regulation_id": regulation_id,
            "violation_count": self.violations[key],
            "max_violations": max_violations,
            "penalty_applied": penalty_applied,
        }

    async def check_entity_compliance(self, entity_id: str) -> dict:
        regs = await gov_db.list_regulations()
        entity_violations = []
        for key, count in self.violations.items():
            if key.startswith(f"{entity_id}:"):
                reg_id = key.split(":")[1]
                entity_violations.append({"regulation_id": reg_id, "count": count})

        return {
            "entity_id": entity_id,
            "total_regulations": len(regs),
            "active_violations": entity_violations,
            "is_compliant": len(entity_violations) == 0,
        }

    async def get_regulation_stats(self) -> dict:
        regs = await gov_db.list_regulations()
        types = {}
        for r in regs:
            rt = r.get("regulation_type", "general")
            if rt not in types:
                types[rt] = 0
            types[rt] += 1
        return {
            "total_regulations": len(regs),
            "by_type": types,
            "total_violations": sum(self.violations.values()),
            "stats": self.stats.copy(),
        }

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "regulation_types": REGULATION_TYPES,
            "active_violations": len(self.violations),
        }


regulation_system = RegulationSystem()
