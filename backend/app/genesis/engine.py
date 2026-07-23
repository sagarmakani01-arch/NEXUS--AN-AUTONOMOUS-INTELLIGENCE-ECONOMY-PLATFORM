import logging

from app.genesis.initialization import genesis_init
from app.genesis.society import society_engine
from app.genesis.mythology import mythology_engine
from app.genesis.philosophy import philosophy_engine
from app.genesis.science import science_engine
from app.genesis.awareness import awareness_engine
from app.genesis.timeline import timeline_engine
from app.genesis.interaction import interaction_engine
from app.genesis.persistence import genesis_db

logger = logging.getLogger("nexus.genesis.engine")


class GenesisEngine:
    def __init__(self):
        self._initialized = False
        self._running = False

    async def initialize(self):
        if self._initialized:
            return
        existing = await genesis_db.list_civilizations()
        if not existing:
            civ = await genesis_init.create_civilization("Primordials")
            logger.info("Genesis civilization created: %s (%s)", civ["name"], civ["id"])
        self._initialized = True

    async def start(self):
        await self.initialize()
        self._running = True
        logger.info("Genesis engine started")

    async def stop(self):
        self._running = False
        logger.info("Genesis engine stopped")

    async def tick(self) -> dict:
        if not self._initialized:
            await self.initialize()

        civs = await genesis_db.list_civilizations()
        results = {}

        for civ in civs:
            if civ["status"] == "extinct":
                continue
            civ_id = civ["id"]
            society_result = await society_engine.tick(civ_id)
            myth_result = await mythology_engine.tick(civ_id)
            phil_result = await philosophy_engine.tick(civ_id)
            sci_result = await science_engine.tick(civ_id)
            aware_result = await awareness_engine.tick(civ_id)
            timeline_result = await timeline_engine.tick(civ_id)
            interaction_result = await interaction_engine.trigger_internal_event(civ_id)

            results[civ_id] = {
                "society": society_result,
                "mythology": myth_result,
                "philosophy": phil_result,
                "science": sci_result,
                "awareness": aware_result,
                "timeline": timeline_result,
                "interaction": interaction_result,
            }

        return results

    async def create_civilization(self, name: str) -> dict:
        return await genesis_init.create_civilization(name)

    async def get_civilization(self, civ_id: str) -> dict | None:
        return await genesis_db.get_civilization(civ_id)

    async def list_civilizations(self) -> list[dict]:
        return await genesis_db.list_civilizations()

    async def get_full_state(self) -> dict:
        civs = await genesis_db.list_civilizations()
        data = {}
        for civ in civs:
            agents = await genesis_db.get_agents(civ["id"])
            beliefs = await genesis_db.get_beliefs(civ["id"])
            philosophies = await genesis_db.get_philosophies(civ["id"])
            discoveries = await genesis_db.get_discoveries(civ["id"])
            eras = await genesis_db.get_eras(civ["id"])
            knowledge = await genesis_db.get_knowledge_domains(civ["id"])
            awareness = await awareness_engine.get_awareness_status(civ["id"])
            data[civ["id"]] = {
                "civilization": civ,
                "agents": agents,
                "beliefs": beliefs,
                "philosophies": philosophies,
                "discoveries": discoveries,
                "eras": eras,
                "knowledge_domains": knowledge,
                "awareness": awareness,
            }
        return {
            "initialized": self._initialized,
            "running": self._running,
            "civilizations": data,
        }


genesis_engine = GenesisEngine()
