import asyncio
import logging
import random
import time

from app.core.event_bus import Event, EventType, dispatch
from app.technology import persistence as db
from app.technology import graph as graph_engine
from app.technology import discovery as discovery_engine
from app.technology import development as development_engine
from app.technology import adoption as adoption_engine
from app.technology import organizations as org_engine
from app.technology import competition as competition_engine
from app.technology import obsolescence as obsolescence_engine
from app.technology import timeline as timeline_engine

logger = logging.getLogger("nexus.technology.engine")


class TechnologyEngine:
    def __init__(self):
        self.running = False
        self.tick_interval = 50
        self.stats = {
            "total_ticks": 0,
            "discoveries": 0,
            "developments_advanced": 0,
            "adoptions": 0,
            "obsoleted": 0,
            "competitions": 0,
        }
        self._initialized = False

    async def start(self):
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize()
        logger.info("Technology engine started (interval=%ds)", self.tick_interval)
        asyncio.create_task(self._loop())

    async def _initialize(self):
        try:
            await graph_engine.initialize_graph()
            for civ_id in ["aetheria", "synthara", "quantos"]:
                await org_engine.initialize_organizations(civ_id)
                existing_level = await db.get_tech_level(civ_id)
                if not existing_level:
                    await db.create_tech_level(
                        civilization_id=civ_id,
                        computational_capability=random.uniform(5.0, 15.0),
                        energy_capability=random.uniform(5.0, 15.0),
                        manufacturing_capability=random.uniform(5.0, 15.0),
                        scientific_knowledge=random.uniform(5.0, 15.0),
                        automation_level=random.uniform(2.0, 8.0),
                        infrastructure_level=random.uniform(5.0, 15.0),
                        current_era="pre_industrial",
                    )
            self._initialized = True
            logger.info("Technology engine initialized")
        except Exception as e:
            logger.exception("Technology engine init error: %s", e)

    async def stop(self):
        self.running = False
        logger.info("Technology engine stopped")

    async def _loop(self):
        while self.running:
            try:
                await self.tick()
            except Exception as e:
                logger.exception("Technology tick error: %s", e)
            await asyncio.sleep(self.tick_interval)

    async def tick(self):
        self.stats["total_ticks"] += 1
        start = time.monotonic()

        for civ_id in ["aetheria", "synthara", "quantos"]:
            try:
                result = await discovery_engine.attempt_discovery(civ_id, method="research")
                if result:
                    self.stats["discoveries"] += 1
            except Exception as e:
                logger.debug("Discovery error for %s: %s", civ_id, e)

            try:
                devs = await db.list_developments(civ_id=civ_id, status="active")
                for dev in devs[:2]:
                    if random.random() > 0.6:
                        await development_engine.advance_development(dev["id"])
                        self.stats["developments_advanced"] += 1
            except Exception as e:
                logger.debug("Development error for %s: %s", civ_id, e)

            try:
                techs = await db.list_technologies(status="prototype")
                if techs and random.random() > 0.7:
                    tech = random.choice(techs)
                    await adoption_engine.evaluate_adoption(civ_id, tech["id"])
                    self.stats["adoptions"] += 1
            except Exception as e:
                logger.debug("Adoption error for %s: %s", civ_id, e)

            try:
                if random.random() > 0.8:
                    await obsolescence_engine.check_obsolescence(civ_id)
            except Exception as e:
                logger.debug("Obsolescence error for %s: %s", civ_id, e)

            try:
                level = await db.get_tech_level(civ_id)
                if level:
                    delta = random.uniform(0.1, 0.5)
                    updates = {}
                    for key in ["computational_capability", "energy_capability", "manufacturing_capability",
                                "scientific_knowledge", "automation_level", "infrastructure_level"]:
                        val = level.get(key, 10.0) + delta * random.uniform(0.5, 1.5)
                        updates[key] = round(min(100.0, val), 2)
                    new_era = await timeline_engine.get_era(civ_id)
                    updates["current_era"] = new_era
                    await db.update_tech_level(civ_id, **updates)
            except Exception as e:
                logger.debug("Tech level update error for %s: %s", civ_id, e)

        if random.random() > 0.5:
            try:
                civs = ["aetheria", "synthara", "quantos"]
                a, b = random.sample(civs, 2)
                await competition_engine.run_competition(a, b)
                self.stats["competitions"] += 1
            except Exception as e:
                logger.debug("Competition error: %s", e)

        await dispatch(Event(EventType.SIMULATION_TICK, {
            "source": "technology_engine",
            "tick": self.stats["total_ticks"],
            "stats": self.stats.copy(),
        }))

        elapsed = time.monotonic() - start
        logger.debug("Technology tick %d completed in %.1fs", self.stats["total_ticks"], elapsed)

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "tick_interval": self.tick_interval,
            "stats": self.stats.copy(),
            "graph": graph_engine.get_state(),
            "discovery": discovery_engine.get_state(),
            "development": development_engine.get_state(),
            "adoption": adoption_engine.get_state(),
            "organizations": org_engine.get_state(),
            "competition": competition_engine.get_state(),
            "obsolescence": obsolescence_engine.get_state(),
            "timeline": timeline_engine.get_state(),
        }

    def set_speed(self, interval: int):
        self.tick_interval = max(10, min(300, interval))
        logger.info("Technology tick interval set to %ds", self.tick_interval)


technology_engine = TechnologyEngine()
