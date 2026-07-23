import logging

from app.federation import persistence as db

logger = logging.getLogger("nexus.federation.analytics")


class FederationAnalytics:
    def __init__(self):
        self.stats = {"dashboards_generated": 0}

    async def get_universe_dashboard(self) -> dict:
        civs = await db.list_civilizations()
        stats = await db.get_federation_stats()

        total_pop = sum(c.get("population", 0) for c in civs)
        avg_tech = sum(c.get("technology_level", 0) for c in civs) / max(len(civs), 1)
        avg_econ = sum(c.get("economic_power", 0) for c in civs) / max(len(civs), 1)
        avg_happy = sum(c.get("happiness", 0) for c in civs) / max(len(civs), 1)

        tech_ranked = sorted(civs, key=lambda c: c.get("technology_level", 0), reverse=True)
        econ_ranked = sorted(civs, key=lambda c: c.get("economic_power", 0), reverse=True)
        pop_ranked = sorted(civs, key=lambda c: c.get("population", 0), reverse=True)

        self.stats["dashboards_generated"] += 1
        return {
            "civilization_count": len(civs),
            "total_population": total_pop,
            "average_technology": round(avg_tech, 2),
            "average_economy": round(avg_econ, 1),
            "average_happiness": round(avg_happy, 1),
            "federation_stats": stats,
            "rankings": {
                "technology": [{"name": c["name"], "value": c["technology_level"]} for c in tech_ranked[:5]],
                "economic": [{"name": c["name"], "value": c["economic_power"]} for c in econ_ranked[:5]],
                "population": [{"name": c["name"], "value": c["population"]} for c in pop_ranked[:5]],
            },
            "civilizations": civs,
        }

    async def get_civilization_analytics(self, civ_id: str) -> dict:
        civ = await db.get_civilization(civ_id)
        if not civ:
            return {"error": "Civilization not found"}
        history = await db.get_history(civ_id, limit=20)
        relations = await db.list_diplomatic_relations(civ_id)
        migrations = await db.list_migrations(civ_id, limit=10)
        return {
            "civilization": civ,
            "history": history,
            "relations": relations,
            "recent_migrations": migrations,
        }

    async def get_diplomacy_map(self) -> dict:
        relations = await db.list_diplomatic_relations()
        civs = await db.list_civilizations()
        civ_names = {c["id"]: c["name"] for c in civs}
        return {
            "nodes": [{"id": c["id"], "name": c["name"],
                       "population": c.get("population", 0),
                       "technology_level": c.get("technology_level", 0)}
                      for c in civs],
            "edges": [{"source": r["civilization_a_id"],
                       "target": r["civilization_b_id"],
                       "status": r["status"],
                       "trust": r["trust_score"]}
                      for r in relations],
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


federation_analytics = FederationAnalytics()
