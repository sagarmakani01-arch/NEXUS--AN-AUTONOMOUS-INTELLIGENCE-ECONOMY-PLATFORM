import logging

from app.governance import persistence as gov_db
from app.governance.authority import authority_system
from app.governance.laws import law_engine
from app.governance.policies import policy_engine
from app.governance.taxation import taxation_system
from app.governance.regulation import regulation_system
from app.governance.conflict import conflict_resolution
from app.governance.voting import voting_system

logger = logging.getLogger("nexus.governance.intelligence")


class GovernanceIntelligence:
    def __init__(self):
        self.stats = {"queries": 0}

    async def get_civilization_dashboard(self) -> dict:
        stats = await gov_db.get_governance_stats()
        entities = await gov_db.list_governance_entities()
        laws = await law_engine.list_laws()
        policies = await policy_engine.list_policies()
        conflicts = await conflict_resolution.get_open_conflicts()
        votes = await voting_system.list_votes("open")
        tax_overview = await taxation_system.get_tax_overview()

        return {
            "stats": stats,
            "entities": {
                "total": len(entities),
                "by_type": self._count_by(entities, "entity_type"),
                "by_authority": self._count_by(entities, "authority_level"),
            },
            "laws": {
                "total": len(laws),
                "by_category": self._count_by(laws, "category"),
                "by_severity": self._count_by(laws, "severity"),
            },
            "policies": {
                "total": len(policies),
                "by_type": self._count_by(policies, "policy_type"),
            },
            "conflicts": {
                "open": len(conflicts),
                "types": self._count_by(conflicts, "conflict_type"),
            },
            "votes": {
                "open": len(votes),
            },
            "taxation": tax_overview,
        }

    async def get_governance_dashboard(self) -> dict:
        laws = await law_engine.list_laws()
        policies = await policy_engine.list_policies()
        votes = await voting_system.list_votes()
        records = await gov_db.get_governance_records(limit=20)

        return {
            "active_laws": len([l for l in laws if l.get("status") == "active"]),
            "active_policies": len([p for p in policies if p.get("status") == "active"]),
            "pending_votes": len([v for v in votes if v.get("status") == "open"]),
            "recent_records": records,
            "law_stats": await law_engine.get_law_stats(),
            "policy_stats": await policy_engine.get_policy_stats(),
            "conflict_stats": conflict_resolution.stats,
            "voting_stats": voting_system.stats,
        }

    async def analyze_economic_data(self) -> dict:
        tax_overview = await taxation_system.get_tax_overview()
        compliance = await regulation_system.check_entity_compliance("system")
        return {
            "taxation": tax_overview,
            "compliance": compliance,
            "recommendations": self._generate_recommendations(tax_overview, compliance),
        }

    def _generate_recommendations(self, tax_overview: dict, compliance: dict) -> list[str]:
        recs = []
        if tax_overview.get("treasury_balance", 0) < 100:
            recs.append("Consider adjusting tax rates to increase treasury revenue")
        if len(tax_overview.get("active_taxes", [])) < 2:
            recs.append("More tax types could diversify revenue streams")
        if not compliance.get("is_compliant", True):
            recs.append("Address compliance violations before expanding regulations")
        return recs

    def _count_by(self, items: list[dict], key: str) -> dict:
        counts = {}
        for item in items:
            val = item.get(key, "unknown")
            if val not in counts:
                counts[val] = 0
            counts[val] += 1
        return counts

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


governance_intelligence = GovernanceIntelligence()
