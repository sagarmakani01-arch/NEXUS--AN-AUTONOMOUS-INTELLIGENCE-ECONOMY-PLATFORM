import asyncio
import logging
import random
import time

from app.core.event_bus import Event, EventType, dispatch
from app.planetary import persistence as db
from app.planetary import planet as planet_engine
from app.planetary import climate as climate_engine
from app.planetary import resources as resources_engine
from app.planetary import infrastructure as infra_engine
from app.planetary import settlements as settlement_engine
from app.planetary import events as event_engine
from app.planetary import sustainability as sustain_engine

logger = logging.getLogger("nexus.planetary.engine")


class PlanetaryEngine:
    def __init__(self):
        self.running = False
        self.tick_interval = 30
        self.stats = {
            "total_ticks": 0,
            "settlements_grew": 0,
            "resources_regenerated": 0,
            "events_triggered": 0,
            "climate_evolutions": 0,
            "infrastructure_ticks": 0,
            "sustainability_calcs": 0,
        }
        self._initialized = False

    async def start(self):
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize()
        logger.info("Planetary engine started (interval=%ds)", self.tick_interval)
        asyncio.create_task(self._loop())

    async def _initialize(self):
        try:
            existing = await db.list_planets()
            if not existing:
                planet_data = await planet_engine.generate_planet("Nexus Prime", seed=42, region_count=16)
                planet_id = planet_data["id"]
                regions = await db.list_regions(planet_id)
                await climate_engine.generate_climate(planet_id, regions, seed=42)

                for civ_id in ["aetheria", "synthara", "quantos"]:
                    region = random.choice(regions) if regions else None
                    if region:
                        await settlement_engine.found_settlement(
                            planet_id, region["id"], civ_id,
                            f"{civ_id.title()} Capital"
                        )
                logger.info("Initialized planet with settlements for 3 civilizations")
            self._initialized = True
        except Exception as e:
            logger.exception("Planetary engine init error: %s", e)

    async def stop(self):
        self.running = False
        logger.info("Planetary engine stopped")

    async def _loop(self):
        while self.running:
            try:
                await self.tick()
            except Exception as e:
                logger.exception("Planetary tick error: %s", e)
            await asyncio.sleep(self.tick_interval)

    async def tick(self):
        self.stats["total_ticks"] += 1
        start = time.monotonic()

        planets = await db.list_planets()
        for planet in planets:
            pid = planet["id"]

            try:
                await settlement_engine.grow_settlements(pid)
                self.stats["settlements_grew"] += 1
            except Exception as e:
                logger.debug("Settlement growth error: %s", e)

            try:
                await resources_engine.regenerate_resources(pid)
                self.stats["resources_regenerated"] += 1
            except Exception as e:
                logger.debug("Resource regen error: %s", e)

            try:
                new_events = await event_engine.check_random_events(pid)
                self.stats["events_triggered"] += len(new_events)
            except Exception as e:
                logger.debug("Event check error: %s", e)

            try:
                await climate_engine.evolve_climate(pid)
                self.stats["climate_evolutions"] += 1
            except Exception as e:
                logger.debug("Climate evolution error: %s", e)

            try:
                await infra_engine.tick_infrastructure(pid)
                self.stats["infrastructure_ticks"] += 1
            except Exception as e:
                logger.debug("Infra tick error: %s", e)

            for civ_id in ["aetheria", "synthara", "quantos"]:
                try:
                    await sustain_engine.calculate_sustainability(pid, civ_id)
                    self.stats["sustainability_calcs"] += 1
                except Exception as e:
                    logger.debug("Sustainability calc error for %s: %s", civ_id, e)

        await dispatch(Event(EventType.SIMULATION_TICK, {
            "source": "planetary_engine",
            "tick": self.stats["total_ticks"],
            "stats": self.stats.copy(),
        }))

        elapsed = time.monotonic() - start
        logger.debug("Planetary tick %d completed in %.1fs", self.stats["total_ticks"], elapsed)

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "tick_interval": self.tick_interval,
            "stats": self.stats.copy(),
            "planet": planet_engine.get_state(),
            "climate": climate_engine.get_state(),
            "resources": resources_engine.get_state(),
            "infrastructure": infra_engine.get_state(),
            "settlements": settlement_engine.get_state(),
            "events": event_engine.get_state(),
            "sustainability": sustain_engine.get_state(),
        }

    def set_speed(self, interval: int):
        self.tick_interval = max(10, min(300, interval))
        logger.info("Planetary tick interval set to %ds", self.tick_interval)


planetary_engine = PlanetaryEngine()
