import json
import uuid

from app.platform.persistence import platform_db
from app.domain.models.platform import Scenario


class ScenarioBuilder:
    """Create custom simulation scenarios with configurable parameters."""

    async def create(self, name: str, description: str, template_id: str = None, author_id: str = None,
                     config: dict = None, is_public: bool = True, tags: list = None) -> dict:
        scenario = Scenario(
            name=name, description=description, template_id=template_id,
            author_id=author_id, is_public=is_public,
            config=json.dumps(config or {}), tags=json.dumps(tags or []),
        )
        saved = await platform_db.create_scenario(scenario)
        return {
            "id": saved.id, "name": saved.name, "description": saved.description,
            "is_public": saved.is_public, "tags": saved.tags,
        }

    async def list_scenarios(self, public: bool = None, author_id: str = None) -> list[dict]:
        scenarios = await platform_db.get_scenarios(public, author_id)
        return [{
            "id": s.id, "name": s.name, "description": s.description, "template_id": s.template_id,
            "author_id": s.author_id, "is_public": s.is_public, "tags": s.tags,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        } for s in scenarios]

    def get_default_config(self) -> dict:
        return {
            "planet": {"size": "medium", "terrain": "mixed", "climate": "temperate", "resources": "abundant"},
            "population": {"initial": 100, "growth_rate": 1.0, "max": 10000},
            "technology": {"starting_level": "stone_age", "research_rate": 1.0},
            "government": {"type": "none", "stability": 0.5},
            "economy": {"type": "barter", "gdp": 100, "tax_rate": 0.1},
            "environment": {"health": 0.8, "pollution": 0.0},
        }


scenario_builder = ScenarioBuilder()
