import asyncio
import logging
import time

from app.core.event_bus import Event, EventType, dispatch
from app.evolution import persistence as evo_db
from app.evolution.population import population_engine
from app.evolution.lineage import lineage_system
from app.evolution.traits import trait_evolution_engine
from app.evolution.skills import skill_inheritance_engine
from app.evolution.mentorship import mentorship_engine
from app.evolution.civilization import civilization_engine
from app.evolution.innovation import innovation_system

logger = logging.getLogger("nexus.evolution.engine")


class EvolutionEngine:
    def __init__(self):
        self.running = False
        self.tick_interval = 60
        self.generation = 0
        self.stats = {
            "total_ticks": 0,
            "civ_evolutions": 0,
            "population_growth": 0,
            "mentorships_formed": 0,
            "innovations_discovered": 0,
        }

    async def start(self):
        if self.running:
            return
        self.running = True
        logger.info("Evolution engine started (interval=%ds)", self.tick_interval)
        asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        logger.info("Evolution engine stopped")

    async def _loop(self):
        while self.running:
            try:
                await self.tick()
            except Exception as e:
                logger.exception("Evolution tick error: %s", e)
            await asyncio.sleep(self.tick_interval)

    async def tick(self):
        self.generation += 1
        self.stats["total_ticks"] += 1
        start = time.monotonic()

        from app.simulation.engine import engine as sim_engine
        agent_count = len(sim_engine.agents)
        company_count = 0
        try:
            from app.organization.engine import organization_engine
            org_state = organization_engine.get_state()
            company_count = org_state.get("stats", {}).get("companies_formed", 0)
        except Exception:
            pass

        open_tasks = 0
        economy_growth = 0.0
        try:
            from app.economy.engine import economy_engine
            eco_state = economy_engine.get_state()
            economy_growth = eco_state.get("stats", {}).get("gdp_growth_rate", 0.0)
        except Exception:
            pass

        try:
            from app.marketplace.engine import marketplace_engine
            mp_state = marketplace_engine.get_state()
            open_tasks = mp_state.get("stats", {}).get("total_tasks", 0)
        except Exception:
            pass

        total_innovations = self.stats["innovations_discovered"]

        pop_need = await population_engine.evaluate_population_need(
            agent_count, company_count, open_tasks, open_tasks, economy_growth
        )
        if pop_need["should_grow"] and pop_need["suggested_growth"] > 0:
            for _ in range(min(pop_need["suggested_growth"], 3)):
                result = await population_engine.generate_citizen()
                if result.get("success"):
                    self.stats["population_growth"] += 1

        innov = await innovation_system.attempt_innovation(
            sim_engine.agents[0].id if sim_engine.agents else ""
        )
        if innov:
            self.stats["innovations_discovered"] += 1

        for agent in sim_engine.agents[:5]:
            mentorships = await evo_db.get_mentorships(mentee_id=agent.id, status="active")
            if not mentorships:
                mentor = await mentorship_engine.find_mentor(agent.id)
                if mentor:
                    await mentorship_engine.create_mentorship(mentor["agent_id"], agent.id)
                    self.stats["mentorships_formed"] += 1

        for agent in sim_engine.agents[:3]:
            active = await evo_db.get_mentorships(mentor_id=agent.id, status="active")
            for m in active:
                await mentorship_engine.conduct_session(m["id"])

        civ_result = await civilization_engine.update_civilization(
            agent_count, company_count, total_innovations, economy_growth
        )
        if civ_result.get("level", 0) > self.generation:
            self.stats["civ_evolutions"] += 1

        await dispatch(Event(EventType.EVOLUTION_TICK, {
            "generation": self.generation,
            "stats": self.stats.copy(),
            "civ_level": civ_result.get("level", 1),
            "population": agent_count,
            "innovations": self.stats["innovations_discovered"],
        }))

        elapsed = time.monotonic() - start
        logger.info(
            "Evolution tick %d completed in %.1fs (pop=%d, civ_level=%d, innovations=%d)",
            self.generation, elapsed, agent_count,
            civ_result.get("level", 1), self.stats["innovations_discovered"],
        )

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "generation": self.generation,
            "tick_interval": self.tick_interval,
            "stats": self.stats.copy(),
            "population": population_engine.get_state(),
            "lineages": lineage_system.get_state(),
            "traits": trait_evolution_engine.get_state(),
            "skills": skill_inheritance_engine.get_state(),
            "mentorship": mentorship_engine.get_state(),
            "civilization": civilization_engine.get_state(),
            "innovation": innovation_system.get_state(),
        }

    def set_speed(self, interval: int):
        self.tick_interval = max(5, min(300, interval))
        logger.info("Evolution tick interval set to %ds", self.tick_interval)


evolution_engine = EvolutionEngine()
