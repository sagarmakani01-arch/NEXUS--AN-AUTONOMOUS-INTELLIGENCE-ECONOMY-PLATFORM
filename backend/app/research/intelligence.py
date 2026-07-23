import json
import logging
import random

from app.research import persistence as db

logger = logging.getLogger("nexus.research.intelligence")


class ResearchIntelligence:
    def __init__(self):
        self.stats = {
            "dashboards_generated": 0,
            "insights_generated": 0,
        }

    async def get_research_dashboard(self) -> dict:
        stats = await db.get_research_stats()
        orgs = await db.list_organizations()
        projects = await db.list_projects()
        techs = await db.list_technologies()
        pubs = await db.list_publications()
        nodes = await db.list_knowledge_nodes(limit=200)

        active_projects = [p for p in projects if p.get("status") in ("active", "proposed")]
        completed_projects = [p for p in projects if p.get("status") == "completed"]
        unlocked_techs = [t for t in techs if t.get("status") == "unlocked"]
        published_papers = [p for p in pubs if p.get("status") == "published"]

        domain_distribution = {}
        for n in nodes:
            d = n.get("domain", "Unknown")
            domain_distribution[d] = domain_distribution.get(d, 0) + 1

        top_orgs = sorted(orgs, key=lambda o: o.get("reputation", 0), reverse=True)[:5]

        self.stats["dashboards_generated"] += 1
        return {
            "stats": stats,
            "active_projects": len(active_projects),
            "completed_projects": len(completed_projects),
            "unlocked_technologies": len(unlocked_techs),
            "published_papers": len(published_papers),
            "knowledge_nodes": len(nodes),
            "domain_distribution": domain_distribution,
            "top_organizations": [{"name": o["name"], "reputation": o["reputation"],
                                   "papers": o.get("published_papers", 0)} for o in top_orgs],
            "recent_projects": projects[:5],
            "recent_innovations": pubs[:5],
        }

    async def get_organization_report(self, org_id: str) -> dict:
        org = await db.get_organization(org_id)
        if not org:
            return {"error": "Organization not found"}

        projects = await db.list_projects(organization_id=org_id)
        innovations = await db.list_research_innovations(organization_id=org_id)
        techs = await db.list_technologies()

        org_techs = [t for t in techs if t.get("organization_id") == org_id]

        return {
            "organization": org,
            "total_projects": len(projects),
            "active_projects": len([p for p in projects if p.get("status") == "active"]),
            "completed_projects": len([p for p in projects if p.get("status") == "completed"]),
            "innovations": len(innovations),
            "technologies": len(org_techs),
            "unlocked_technologies": len([t for t in org_techs if t.get("status") == "unlocked"]),
            "total_citations": org.get("citations_received", 0),
            "published_papers": org.get("published_papers", 0),
        }

    async def get_research_trends(self) -> dict:
        nodes = await db.list_knowledge_nodes(limit=200)
        domain_counts = {}
        recent_discoveries = []
        for n in nodes:
            d = n.get("domain", "Unknown")
            domain_counts[d] = domain_counts.get(d, 0) + 1
            if n.get("novelty_score", 0) > 0.7:
                recent_discoveries.append(n)

        sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)
        return {
            "top_domains": [{"domain": d, "nodes": c} for d, c in sorted_domains[:10]],
            "emerging_fields": sorted_domains[-3:] if len(sorted_domains) >= 3 else sorted_domains,
            "high_novelty_count": len(recent_discoveries),
            "total_knowledge_nodes": len(nodes),
        }

    async def get_citation_network(self) -> dict:
        pubs = await db.list_publications()
        cited = [p for p in pubs if p.get("citations", 0) > 0]
        cited.sort(key=lambda p: p.get("citations", 0), reverse=True)
        return {
            "total_publications": len(pubs),
            "cited_publications": len(cited),
            "top_cited": cited[:10],
            "average_citations": round(
                sum(p.get("citations", 0) for p in pubs) / max(len(pubs), 1), 1
            ),
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


research_intelligence = ResearchIntelligence()
