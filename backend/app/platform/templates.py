import json
import random

from app.platform.persistence import platform_db
from app.domain.models.platform import SimulationTemplate


class TemplateManager:
    """Simulation templates for starting civilizations with different initial conditions."""

    TEMPLATES = [
        {
            "name": "Industrial Civilization", "type": "industrial",
            "desc": "Start as an industrial-age civilization focused on manufacturing, trade, and economic growth.",
            "initial": {"population": 500, "starting_tech": "steam_power", "economy": "industrial", "government": "representative"},
            "rules": {"trade_enabled": True, "research_rate": 1.0, "growth_rate": 1.2, "resource_consumption": 1.5},
            "environment": {"terrain": "plains", "resources": "abundant", "climate": "temperate"},
            "objectives": ["Build 10 factories", "Achieve GDP of 10000", "Research electricity"],
            "difficulty": "easy",
        },
        {
            "name": "Research Civilization", "type": "research",
            "desc": "A knowledge-focused civilization prioritizing science, education, and technological advancement.",
            "initial": {"population": 300, "starting_tech": "writing", "economy": "knowledge", "government": "academy"},
            "rules": {"trade_enabled": True, "research_rate": 2.0, "growth_rate": 0.8, "resource_consumption": 0.7},
            "environment": {"terrain": "coastal", "resources": "moderate", "climate": "mediterranean"},
            "objectives": ["Research 20 technologies", "Establish 3 universities", "Publish 50 research papers"],
            "difficulty": "medium",
        },
        {
            "name": "Resource-Limited Planet", "type": "survival",
            "desc": "Survive on a planet with scarce resources. Every decision about resource extraction matters.",
            "initial": {"population": 100, "starting_tech": "basic_tools", "economy": "survival", "government": "council"},
            "rules": {"trade_enabled": False, "research_rate": 0.5, "growth_rate": 0.5, "resource_consumption": 0.3},
            "environment": {"terrain": "desert", "resources": "scarce", "climate": "harsh"},
            "objectives": ["Reach population of 500", "Discover 3 new resources", "Build irrigation system"],
            "difficulty": "hard",
        },
        {
            "name": "Ocean Civilization", "type": "aquatic",
            "desc": "Build a civilization on a water world. Develop underwater cities and aquatic technologies.",
            "initial": {"population": 200, "starting_tech": "underwater_construction", "economy": "aquatic", "government": "fleet_council"},
            "rules": {"trade_enabled": True, "research_rate": 1.2, "growth_rate": 0.9, "resource_consumption": 0.8},
            "environment": {"terrain": "ocean", "resources": "marine_abundant", "climate": "tropical"},
            "objectives": ["Build 5 underwater cities", "Develop marine biotechnology", "Explore the ocean floor"],
            "difficulty": "medium",
        },
        {
            "name": "Space Civilization", "type": "space",
            "desc": "Begin as a spacefaring civilization with orbital colonies and interstellar ambitions.",
            "initial": {"population": 1000, "starting_tech": "space_travel", "economy": "stellar", "government": "federation"},
            "rules": {"trade_enabled": True, "research_rate": 1.5, "growth_rate": 1.0, "resource_consumption": 1.2},
            "environment": {"terrain": "orbital", "resources": "asteroid_rich", "climate": "controlled"},
            "objectives": ["Colonize 3 planets", "Establish interstellar trade", "Achieve FTL travel"],
            "difficulty": "hard",
        },
        {
            "name": "Experimental Society", "type": "experimental",
            "desc": "An experimental society where you define the rules. Start fresh with customizable parameters.",
            "initial": {"population": 50, "starting_tech": "none", "economy": "barter", "government": "none"},
            "rules": {"trade_enabled": True, "research_rate": 1.0, "growth_rate": 1.0, "resource_consumption": 1.0},
            "environment": {"terrain": "random", "resources": "random", "climate": "random"},
            "objectives": ["Define your own path", "Achieve civilization milestone", "Write your history"],
            "difficulty": "custom",
        },
    ]

    async def seed(self) -> list[dict]:
        results = []
        for t in self.TEMPLATES:
            existing = await platform_db.get_templates(t["type"])
            if any(x.name == t["name"] for x in existing):
                continue
            tmpl = SimulationTemplate(
                name=t["name"], description=t["desc"], template_type=t["type"],
                initial_conditions=json.dumps(t["initial"]), rules=json.dumps(t["rules"]),
                environment=json.dumps(t["environment"]), objectives=json.dumps(t["objectives"]),
                difficulty=t["difficulty"], author="nexus",
            )
            saved = await platform_db.create_template(tmpl)
            results.append({"id": saved.id, "name": saved.name, "type": saved.template_type})
        return results

    async def list_templates(self, template_type: str = None) -> list[dict]:
        templates = await platform_db.get_templates(template_type)
        return [{
            "id": t.id, "name": t.name, "description": t.description, "type": t.template_type,
            "difficulty": t.difficulty, "objectives": t.objectives,
        } for t in templates]


template_manager = TemplateManager()
