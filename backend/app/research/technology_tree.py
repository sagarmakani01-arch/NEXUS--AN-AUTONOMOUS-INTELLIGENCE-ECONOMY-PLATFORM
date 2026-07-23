import json
import logging
import random

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.technology")

TECH_CATEGORIES = {
    "computing": ["Quantum Processor", "Neural Computing Unit", "Distributed Computing Grid",
                  "Optical Computing", "DNA Storage"],
    "biotech": ["Gene Therapy Kit", "Protein Synthesizer", "Bioinformatics Platform",
                "Synthetic Organism Designer", "Neural Interface"],
    "materials": ["Self-Healing Material", "Superconductor", "Nanobot Swarm",
                  "Programmable Matter", "Energy Storage Crystal"],
    "energy": ["Fusion Reactor", "Solar Collector Array", "Wireless Power Grid",
               "Zero-Point Energy Tap", "Antimatter Containment"],
    "ai": ["General Intelligence Core", "Swarm Intelligence Network", "Causal Reasoning Engine",
           "Creative Synthesis System", "Autonomous Research AI"],
    "space": ["Faster-Than-Light Drive", "Orbital Habitat", "Asteroid Mining System",
              "Terraforming Engine", "Interstellar Probe"],
}


class TechnologyTreeEngine:
    def __init__(self):
        self.stats = {
            "technologies_created": 0,
            "technologies_unlocked": 0,
            "total_adoption": 0,
            "research_points_earned": 0,
        }

    async def initialize_tech_tree(self) -> dict:
        created = []
        for category, techs in TECH_CATEGORIES.items():
            for i, tech_name in enumerate(techs):
                prereqs = []
                if i > 0:
                    prev_techs = TECH_CATEGORIES[category]
                    prereqs.append(prev_techs[i - 1])

                tech_id = await db.create_technology(
                    name=tech_name, tech_type=category,
                    domain=category,
                    difficulty_level=i + 1,
                    prerequisites=json.dumps(prereqs),
                    benefits=json.dumps([f"Unlocks {tech_name} capabilities"]),
                    development_cost=random.uniform(50, 200),
                    research_points_needed=random.randint(100, 500),
                )
                self.stats["technologies_created"] += 1
                created.append(tech_id)

        return {"total_technologies": len(created)}

    async def contribute_research(self, tech_id: str, agent_id: str,
                                  points: int = 10) -> dict:
        tech = await db.get_technology(tech_id)
        if not tech:
            return {"success": False, "error": "Technology not found"}
        if tech["status"] == "unlocked":
            return {"success": False, "error": "Already unlocked"}

        prereqs = tech.get("prerequisites", [])
        for prereq_name in prereqs:
            all_techs = await db.list_technologies()
            prereq_tech = next((t for t in all_techs if t["name"] == prereq_name), None)
            if prereq_tech and prereq_tech["status"] != "unlocked":
                return {"success": False, "error": f"Prerequisite not met: {prereq_name}"}

        new_earned = tech["research_points_earned"] + points
        new_maturity = min(1.0, new_earned / tech["research_points_needed"])
        await db.update_technology(
            tech_id, research_points_earned=new_earned,
            maturity=round(new_maturity, 3),
        )
        self.stats["research_points_earned"] += points

        unlocked = False
        if new_earned >= tech["research_points_needed"]:
            await db.update_technology(
                tech_id, status="unlocked",
                unlocked_at=datetime.now(timezone.utc).isoformat() if hasattr(datetime, 'now') else None,
            )
            unlocked = True
            self.stats["technologies_unlocked"] += 1
            await dispatch(Event(EventType.TECHNOLOGY_UNLOCKED, {
                "technology_id": tech_id, "name": tech["name"],
                "type": tech["tech_type"], "agent_id": agent_id,
            }))

        return {
            "success": True, "research_points_earned": new_earned,
            "maturity": round(new_maturity, 3), "unlocked": unlocked,
        }

    async def adopt_technology(self, tech_id: str, organization_id: str) -> dict:
        tech = await db.get_technology(tech_id)
        if not tech or tech["status"] != "unlocked":
            return {"success": False, "error": "Technology not available"}
        new_count = tech["adoption_count"] + 1
        await db.update_technology(tech_id, adoption_count=new_count)
        self.stats["total_adoption"] += 1
        return {"success": True, "adoption_count": new_count}

    async def get_tech_tree(self, domain: str | None = None) -> list[dict]:
        return await db.list_technologies(domain=domain)

    async def get_technology(self, tech_id: str) -> dict | None:
        return await db.get_technology(tech_id)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


from datetime import datetime, timezone  # noqa: E402


technology_tree_engine = TechnologyTreeEngine()
