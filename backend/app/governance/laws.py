import logging
from datetime import datetime, timezone

from app.governance import persistence as gov_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.laws")

LAW_CATEGORIES = [
    "economic", "social", "resource", "labor", "technology",
    "environmental", "security", "trade", "intellectual_property",
]
SEVERITY_LEVELS = ["low", "medium", "high", "critical"]


class LawEngine:
    def __init__(self):
        self.stats = {
            "laws_created": 0,
            "laws_enforced": 0,
            "violations_detected": 0,
        }

    async def create_law(self, name: str, description: str | None, creator_id: str,
                         scope: str = "global", category: str = "general",
                         severity: str = "medium",
                         affected_entities: list[str] | None = None,
                         penalty: dict | None = None) -> dict:
        if category not in LAW_CATEGORIES:
            category = "general"
        if severity not in SEVERITY_LEVELS:
            severity = "medium"

        law_id = await gov_db.create_law(
            name=name, description=description, creator_id=creator_id,
            scope=scope, category=category, severity=severity,
            affected_entities=affected_entities, penalty=penalty,
        )
        self.stats["laws_created"] += 1

        await gov_db.record_governance(
            record_type="law_created", title=f"New Law: {name}",
            actor_id=creator_id, description=description,
            related_ids=[law_id],
            impact={"category": category, "severity": severity},
        )

        await dispatch(Event(EventType.LAW_CREATED, {
            "law_id": law_id, "name": name,
            "creator_id": creator_id, "category": category,
            "severity": severity, "scope": scope,
        }))

        return {
            "law_id": law_id,
            "name": name,
            "category": category,
            "severity": severity,
            "scope": scope,
            "status": "active",
        }

    async def get_law(self, law_id: str) -> dict | None:
        return await gov_db.get_law(law_id)

    async def list_laws(self, category: str | None = None) -> list[dict]:
        return await gov_db.list_laws(category)

    async def check_compliance(self, entity_id: str) -> dict:
        laws = await gov_db.list_laws()
        regulations = await gov_db.list_regulations()
        policies = await gov_db.list_policies()

        violations = []
        for law in laws:
            affected = law.get("affected_entities", [])
            if not affected or entity_id in affected:
                self.stats["laws_enforced"] += 1

        for reg in regulations:
            sector = reg.get("target_sector")
            if not sector:
                self.stats["violations_detected"] += 1

        return {
            "entity_id": entity_id,
            "total_laws": len(laws),
            "total_regulations": len(regulations),
            "total_policies": len(policies),
            "violations": violations,
            "compliant": len(violations) == 0,
        }

    async def get_law_stats(self) -> dict:
        laws = await gov_db.list_laws()
        categories = {}
        for law in laws:
            cat = law.get("category", "general")
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        return {
            "total_laws": len(laws),
            "by_category": categories,
            "stats": self.stats.copy(),
        }

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "categories": LAW_CATEGORIES,
            "severity_levels": SEVERITY_LEVELS,
        }


law_engine = LawEngine()
