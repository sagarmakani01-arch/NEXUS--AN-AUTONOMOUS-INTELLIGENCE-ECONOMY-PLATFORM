import random
from datetime import datetime

from app.meta.persistence import meta_persistence
from app.domain.models.meta import UniverseObservation


class UniverseObservatory:
    """Monitors all civilizations and captures state snapshots for analysis."""

    def __init__(self):
        self._observation_count = 0

    async def observe(
        self,
        simulation_id: str,
        tick: int,
        year: int,
        civilization_id: str = None,
        population: int = 0,
        economy_gdp: float = 0.0,
        research_level: float = 0.0,
        technology_level: float = 0.0,
        education_index: float = 0.0,
        governance_stability: float = 0.0,
        environment_health: float = 0.0,
        innovation_rate: float = 0.0,
        social_stability: float = 0.0,
        resource_scarcity: float = 0.0,
        event_count: int = 0,
    ) -> dict:
        obs = UniverseObservation(
            simulation_id=simulation_id,
            tick=tick,
            year=year,
            civilization_id=civilization_id,
            population=population,
            economy_gdp=economy_gdp,
            research_level=research_level,
            technology_level=technology_level,
            education_index=education_index,
            governance_stability=governance_stability,
            environment_health=environment_health,
            innovation_rate=innovation_rate,
            social_stability=social_stability,
            resource_scarcity=resource_scarcity,
            event_count=event_count,
        )
        saved = await meta_persistence.create_observation(obs)
        self._observation_count += 1
        return {"id": saved.id, "tick": tick, "year": year, "population": population}

    async def get_trend(self, simulation_id: str, metric: str, span: int = 50) -> list[dict]:
        observations = await meta_persistence.get_observations(simulation_id, limit=span)
        metric_map = {
            "population": "population",
            "economy": "economy_gdp",
            "research": "research_level",
            "technology": "technology_level",
            "education": "education_index",
            "governance": "governance_stability",
            "environment": "environment_health",
            "innovation": "innovation_rate",
            "stability": "social_stability",
            "resources": "resource_scarcity",
        }
        attr = metric_map.get(metric, "population")
        result = []
        for obs in reversed(observations):
            result.append({
                "tick": obs.tick,
                "year": obs.year,
                "value": getattr(obs, attr, 0),
            })
        return result

    async def get_latest_observation(self, simulation_id: str) -> Optional[dict]:
        observations = await meta_persistence.get_observations(simulation_id, limit=1)
        if not observations:
            return None
        obs = observations[0]
        return {
            "id": obs.id,
            "tick": obs.tick,
            "year": obs.year,
            "population": obs.population,
            "economy_gdp": obs.economy_gdp,
            "research_level": obs.research_level,
            "technology_level": obs.technology_level,
            "education_index": obs.education_index,
            "governance_stability": obs.governance_stability,
            "environment_health": obs.environment_health,
            "innovation_rate": obs.innovation_rate,
            "social_stability": obs.social_stability,
            "resource_scarcity": obs.resource_scarcity,
            "event_count": obs.event_count,
        }

    def get_count(self) -> int:
        return self._observation_count


observatory = UniverseObservatory()
