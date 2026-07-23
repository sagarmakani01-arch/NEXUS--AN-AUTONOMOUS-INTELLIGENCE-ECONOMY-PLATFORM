from app.meta.observatory import observatory
from app.meta.analysis import analyzer
from app.meta.patterns import pattern_engine
from app.meta.evaluation import evaluator
from app.meta.experiments import experiment_manager
from app.meta.recommendations import recommender
from app.meta.knowledge import knowledge_base
from app.meta.explainability import explainer
from app.meta.persistence import meta_persistence


class MetaEngine:
    """Orchestrates the meta intelligence layer for NEXUS."""

    def __init__(self):
        self._initialized = False
        self._running = False

    async def initialize(self):
        if self._initialized:
            return
        self._initialized = True

    async def start(self):
        await self.initialize()
        self._running = True

    async def stop(self):
        self._running = False

    async def tick(self, full_world_state: dict = None) -> dict:
        if not self._initialized:
            await self.initialize()
        return {"observations": observatory.get_count(), "patterns": pattern_engine.get_discovery_count()}

    async def observe(self, simulation_id: str, tick: int, year: int, world_state: dict = None) -> dict:
        if not world_state:
            return {"observed": False}

        return await observatory.observe(
            simulation_id=simulation_id,
            tick=tick,
            year=year,
            population=world_state.get("population", 0) if isinstance(world_state, dict) else 0,
            economy_gdp=world_state.get("economy", {}).get("gdp", 0)
            if isinstance(world_state.get("economy"), dict) else 0,
            event_count=world_state.get("total_events", 0) if isinstance(world_state, dict) else 0,
        )

    async def get_full_state(self) -> dict:
        return {
            "initialized": self._initialized,
            "running": self._running,
            "observations": observatory.get_count(),
            "patterns": pattern_engine.get_discovery_count(),
            "recommendations": await recommender.get_stats(),
            "knowledge": await knowledge_base.get_stats(),
        }

    async def discover_patterns(self) -> list[dict]:
        return await pattern_engine.discover_patterns()

    async def evaluate_rules(self, rule_name: str = None) -> list[dict]:
        return await evaluator.evaluate(rule_name)

    async def generate_recommendations(self, domain: str = None) -> list[dict]:
        return await recommender.generate_recommendations(domain)

    async def compare_simulations(self, sim_a: str, sim_b: str) -> list[dict]:
        obs_a = await meta_persistence.get_observations(sim_a, limit=1)
        obs_b = await meta_persistence.get_observations(sim_b, limit=1)
        return await analyzer.compare(sim_a, sim_b, obs_a, obs_b)


meta_engine = MetaEngine()
