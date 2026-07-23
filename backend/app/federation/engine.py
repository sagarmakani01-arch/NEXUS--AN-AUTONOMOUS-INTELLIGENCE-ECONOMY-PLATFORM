import asyncio
import logging
import random
import time

from app.core.event_bus import Event, EventType, dispatch
from app.federation import persistence as db
from app.federation.civilizations import civilization_manager
from app.federation.diplomacy import diplomacy_engine
from app.federation.trade import trade_engine
from app.federation.knowledge import knowledge_exchange_engine
from app.federation.competition import competition_engine
from app.federation.migration import migration_engine
from app.federation.council import federation_council_manager
from app.federation.analytics import federation_analytics

logger = logging.getLogger("nexus.federation.engine")


class FederationEngine:
    def __init__(self):
        self.running = False
        self.tick_interval = 90
        self.stats = {
            "total_ticks": 0,
            "auto_diplomacy": 0,
            "auto_trade": 0,
            "auto_migrations": 0,
            "auto_competitions": 0,
        }
        self._initialized = False

    async def start(self):
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize()
        logger.info("Federation engine started (interval=%ds)", self.tick_interval)
        asyncio.create_task(self._loop())

    async def _initialize(self):
        try:
            civs = await db.list_civilizations()
            if len(civs) < 2:
                for i, name in enumerate(["Aethoria Prime", "Borealis Union", "Cyberia Collective"]):
                    await civilization_manager.create_civilization(
                        name=name,
                        government_type=["centralized", "distributed", "meritocratic"][i],
                        economic_model=["free_market", "resource_controlled", "research_focused"][i],
                        population=random.randint(80, 200),
                    )
                civs = await db.list_civilizations()

            if len(civs) >= 2:
                relations = await db.list_diplomatic_relations()
                if len(relations) < len(civs):
                    for i in range(len(civs)):
                        for j in range(i + 1, len(civs)):
                            existing = await db.get_diplomatic_relation(civs[i]["id"], civs[j]["id"])
                            if not existing:
                                status = random.choice(["neutral", "friendly", "competitive"])
                                await diplomacy_engine.establish_relation(
                                    civs[i]["id"], civs[j]["id"], status)

            councils = await db.list_federation_councils()
            if not councils:
                civs = await db.list_civilizations()
                if civs:
                    council = await federation_council_manager.create_council(
                        "NEXUS Federation Council",
                        civs[0]["id"],
                        "Governing body for inter-civilization cooperation",
                    )
                    for c in civs[1:4]:
                        await federation_council_manager.join_council(council["council_id"], c["id"])

            self._initialized = True
        except Exception as e:
            logger.exception("Federation init error: %s", e)

    async def stop(self):
        self.running = False
        logger.info("Federation engine stopped")

    async def _loop(self):
        while self.running:
            try:
                await self.tick()
            except Exception as e:
                logger.exception("Federation tick error: %s", e)
            await asyncio.sleep(self.tick_interval)

    async def tick(self):
        self.stats["total_ticks"] += 1
        start = time.monotonic()

        civs = await db.list_civilizations()

        for civ in civs:
            try:
                await civilization_manager.tick_civilization(civ["id"])
            except Exception:
                pass

        try:
            if random.random() > 0.6 and len(civs) >= 2:
                a, b = random.sample(civs, 2)
                existing = await db.get_diplomatic_relation(a["id"], b["id"])
                if existing and random.random() > 0.7:
                    new_status = random.choice(["friendly", "competitive", "neutral"])
                    await diplomacy_engine.update_relation(a["id"], b["id"], new_status)
                    self.stats["auto_diplomacy"] += 1
        except Exception:
            pass

        try:
            if random.random() > 0.5 and len(civs) >= 2:
                a, b = random.sample(civs, 2)
                await trade_engine.create_trade(a["id"], b["id"])
                self.stats["auto_trade"] += 1
        except Exception:
            pass

        try:
            await trade_engine.tick_trades()
        except Exception:
            pass

        try:
            if random.random() > 0.8 and len(civs) >= 2:
                a, b = random.sample(civs, 2)
                await competition_engine.run_competition(a["id"], b["id"])
                self.stats["auto_competitions"] += 1
        except Exception:
            pass

        try:
            if random.random() > 0.85 and len(civs) >= 2:
                origin, dest = random.sample(civs, 2)
                agent_id = f"migrant_{random.randint(1000, 9999)}"
                await migration_engine.process_migration(agent_id, origin["id"], dest["id"])
                self.stats["auto_migrations"] += 1
        except Exception:
            pass

        await dispatch(Event(EventType.SIMULATION_TICK, {
            "tick": self.stats["total_ticks"], "federation_stats": self.stats.copy(),
        }))

        elapsed = time.monotonic() - start
        logger.debug("Federation tick %d completed in %.1fs", self.stats["total_ticks"], elapsed)

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "tick_interval": self.tick_interval,
            "stats": self.stats.copy(),
            "civilizations": civilization_manager.get_state(),
            "diplomacy": diplomacy_engine.get_state(),
            "trade": trade_engine.get_state(),
            "knowledge": knowledge_exchange_engine.get_state(),
            "competition": competition_engine.get_state(),
            "migration": migration_engine.get_state(),
            "council": federation_council_manager.get_state(),
            "analytics": federation_analytics.get_state(),
        }

    def set_speed(self, interval: int):
        self.tick_interval = max(30, min(300, interval))
        logger.info("Federation tick interval set to %ds", self.tick_interval)


federation_engine = FederationEngine()
