import asyncio
import logging
import random
import time

from app.core.event_bus import Event, EventType, dispatch
from app.culture import persistence as db
from app.culture import identity as identity_engine
from app.culture import values as values_engine
from app.culture import traditions as traditions_engine
from app.culture import institutions as institutions_engine
from app.culture import communities as communities_engine
from app.culture import memory as memory_engine
from app.culture import dynamics as dynamics_engine
from app.culture import reputation as reputation_engine
from app.culture import evolution as evolution_engine

logger = logging.getLogger("nexus.culture.engine")


class CultureEngine:
    def __init__(self):
        self.running = False
        self.tick_interval = 60
        self.stats = {
            "total_ticks": 0,
            "value_shifts": 0,
            "traditions_held": 0,
            "norms_emerged": 0,
            "institutions_founded": 0,
            "communities_grew": 0,
            "memories_recorded": 0,
            "identity_scores_calculated": 0,
        }
        self._initialized = False

    async def start(self):
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize()
        logger.info("Culture engine started (interval=%ds)", self.tick_interval)
        asyncio.create_task(self._loop())

    async def _initialize(self):
        try:
            for civ_id in ["aetheria", "synthara", "quantos"]:
                await identity_engine.initialize_identity(civ_id)
                await values_engine.initialize_values(civ_id)
                await traditions_engine.initialize_traditions(civ_id)
                await institutions_engine.initialize_institutions(civ_id)
                await communities_engine.initialize_communities(civ_id)
                await dynamics_engine.initialize_dynamics(civ_id)
            self._initialized = True
            logger.info("Culture engine initialized for 3 civilizations")
        except Exception as e:
            logger.exception("Culture engine init error: %s", e)

    async def stop(self):
        self.running = False
        logger.info("Culture engine stopped")

    async def _loop(self):
        while self.running:
            try:
                await self.tick()
            except Exception as e:
                logger.exception("Culture tick error: %s", e)
            await asyncio.sleep(self.tick_interval)

    async def tick(self):
        self.stats["total_ticks"] += 1
        start = time.monotonic()

        for civ_id in ["aetheria", "synthara", "quantos"]:
            try:
                event_types = ["discovery", "trade_deal", "education", "innovation", "crisis"]
                event = random.choice(event_types)
                await values_engine.apply_event_influence(civ_id, event)
                self.stats["value_shifts"] += 1
            except Exception as e:
                logger.debug("Value shift error for %s: %s", civ_id, e)

            try:
                due = await traditions_engine.check_traditions(civ_id)
                if due:
                    self.stats["traditions_held"] += len(due)
            except Exception as e:
                logger.debug("Tradition check error for %s: %s", civ_id, e)

            try:
                result = await evolution_engine.evolve_social_norms(civ_id)
                if result.get("new_norm"):
                    self.stats["norms_emerged"] += 1
            except Exception as e:
                logger.debug("Norm evolution error for %s: %s", civ_id, e)

            try:
                await communities_engine.grow_communities(civ_id)
                self.stats["communities_grew"] += 1
            except Exception as e:
                logger.debug("Community growth error for %s: %s", civ_id, e)

            try:
                await dynamics_engine.tick_dynamics(civ_id)
            except Exception as e:
                logger.debug("Dynamics tick error for %s: %s", civ_id, e)

            try:
                await evolution_engine.evolve_values(civ_id)
                await evolution_engine.evolve_institutions(civ_id)
            except Exception as e:
                logger.debug("Evolution tick error for %s: %s", civ_id, e)

            try:
                await evolution_engine.calculate_identity_score(civ_id)
                self.stats["identity_scores_calculated"] += 1
            except Exception as e:
                logger.debug("Identity score error for %s: %s", civ_id, e)

        await dispatch(Event(EventType.SIMULATION_TICK, {
            "source": "culture_engine",
            "tick": self.stats["total_ticks"],
            "stats": self.stats.copy(),
        }))

        elapsed = time.monotonic() - start
        logger.debug("Culture tick %d completed in %.1fs", self.stats["total_ticks"], elapsed)

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "tick_interval": self.tick_interval,
            "stats": self.stats.copy(),
            "identity": identity_engine.get_state(),
            "values": values_engine.get_state(),
            "traditions": traditions_engine.get_state(),
            "institutions": institutions_engine.get_state(),
            "communities": communities_engine.get_state(),
            "memory": memory_engine.get_state(),
            "dynamics": dynamics_engine.get_state(),
            "reputation": reputation_engine.get_state(),
            "evolution": evolution_engine.get_state(),
        }

    def set_speed(self, interval: int):
        self.tick_interval = max(10, min(300, interval))
        logger.info("Culture tick interval set to %ds", self.tick_interval)


culture_engine = CultureEngine()
