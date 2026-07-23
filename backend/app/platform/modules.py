import json
import random

from app.platform.persistence import platform_db
from app.domain.models.platform import ExtensionModule


class ModuleMarketplace:
    """Registry for community extensions and modules."""

    MODULE_PRESETS = [
        {"name": "advanced_economy_v2", "display_name": "Advanced Economy v2", "cat": "economy", "desc": "Complete economic overhaul with supply chains, inflation, and international trade.", "author": "Nexus Labs"},
        {"name": "civilization_rules", "display_name": "New Civilization Rules", "cat": "governance", "desc": "Alternative governance models including AI-led, anarchist, and corporate states.", "author": "SimForge"},
        {"name": "alt_education", "display_name": "Alternative Education", "cat": "social", "desc": "Alternative education system with apprenticeships, online learning, and skill-based progression.", "author": "EduLab"},
        {"name": "visualization_engine", "display_name": "Visualization Engine Pro", "cat": "visualization", "desc": "Real-time 3D visualization with heat maps, flow diagrams, and population density.", "author": "VisCore"},
        {"name": "scientific_sim", "display_name": "Scientific Simulation", "cat": "research", "desc": "Detailed scientific research module with peer review, replication, and funding cycles.", "author": "SciSim"},
        {"name": "biosphere", "display_name": "Biosphere Dynamics", "cat": "environmental", "desc": "Living biosphere with species evolution, ecosystems, and biodiversity tracking.", "author": "EcoSys"},
        {"name": "cultural_evolution", "display_name": "Cultural Evolution Plus", "cat": "social", "desc": "Enhanced cultural evolution with art, music, religion, and philosophical movements.", "author": "CultGen"},
        {"name": "military_conflict", "display_name": "Military & Conflict", "cat": "governance", "desc": "Detailed warfare simulation with strategy, logistics, diplomacy, and peace treaties.", "author": "WarSim"},
    ]

    async def seed_modules(self) -> list[dict]:
        results = []
        for m in self.MODULE_PRESETS:
            existing = await platform_db.get_modules(m["cat"])
            if any(x.name == m["name"] for x in existing):
                continue
            mod = ExtensionModule(name=m["name"], display_name=m["display_name"], description=m["desc"], author=m["author"], category=m["cat"], version="1.0.0", downloads=random.randint(10, 500), rating=round(random.uniform(3.0, 5.0), 1))
            saved = await platform_db.create_module(mod)
            results.append({"id": saved.id, "name": saved.name, "category": saved.category, "rating": saved.rating, "downloads": saved.downloads})
        return results

    async def list_modules(self, category: str = None) -> list[dict]:
        modules = await platform_db.get_modules(category)
        return [{
            "id": m.id, "name": m.name, "display_name": m.display_name, "description": m.description,
            "author": m.author, "version": m.version, "category": m.category, "license": m.license,
            "downloads": m.downloads, "rating": m.rating, "compatibility": m.compatibility,
        } for m in modules]

    async def get_stats(self) -> dict:
        modules = await platform_db.get_modules()
        cats = {}
        for m in modules:
            cats[m.category] = cats.get(m.category, 0) + 1
        avg_rating = sum(m.rating for m in modules) / max(1, len(modules))
        return {"total": len(modules), "categories": cats, "average_rating": round(avg_rating, 1), "total_downloads": sum(m.downloads for m in modules)}


marketplace = ModuleMarketplace()
