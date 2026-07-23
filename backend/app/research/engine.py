import asyncio
import logging
import time

from app.core.event_bus import Event, EventType, dispatch
from app.research import persistence as db
from app.research.organizations import organization_manager
from app.research.projects import project_manager
from app.research.knowledge_graph import knowledge_graph_engine
from app.research.experiments import experiment_engine
from app.research.publications import publication_engine
from app.research.peer_review import peer_review_engine
from app.research.technology_tree import technology_tree_engine
from app.research.diffusion import knowledge_diffusion_engine
from app.research.funding import funding_engine
from app.research.innovation import research_innovation_engine
from app.research.intelligence import research_intelligence

logger = logging.getLogger("nexus.research.engine")


class ResearchEngine:
    def __init__(self):
        self.running = False
        self.tick_interval = 45
        self.stats = {
            "total_ticks": 0,
            "auto_projects": 0,
            "auto_experiments": 0,
            "auto_publications": 0,
            "tech_contributions": 0,
        }
        self._initialized = False

    async def start(self):
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize()
        logger.info("Research engine started (interval=%ds)", self.tick_interval)
        asyncio.create_task(self._loop())

    async def _initialize(self):
        try:
            existing_techs = await db.list_technologies()
            if len(existing_techs) < 5:
                await technology_tree_engine.initialize_tech_tree()
                logger.info("Initialized technology tree with default technologies")

            existing_orgs = await db.list_organizations()
            if len(existing_orgs) < 2:
                for org_type in ["university", "corporate_lab", "government_institute"]:
                    await organization_manager.create_organization(
                        name=f"NEXUS {org_type.replace('_', ' ').title()}",
                        org_type=org_type,
                    )
                logger.info("Initialized default research organizations")

            existing_nodes = await db.list_knowledge_nodes()
            if len(existing_nodes) < 5:
                for domain in ["Artificial Intelligence", "Quantum Computing", "Biotechnology"]:
                    await knowledge_graph_engine.auto_populate_domain(domain)
                logger.info("Initialized knowledge graph with default domains")

            self._initialized = True
        except Exception as e:
            logger.exception("Research engine init error: %s", e)

    async def stop(self):
        self.running = False
        logger.info("Research engine stopped")

    async def _loop(self):
        while self.running:
            try:
                await self.tick()
            except Exception as e:
                logger.exception("Research tick error: %s", e)
            await asyncio.sleep(self.tick_interval)

    async def tick(self):
        self.stats["total_ticks"] += 1
        start = time.monotonic()

        try:
            active_projects = await db.list_projects(status="active")
            if len(active_projects) < 3 and random.random() > 0.5:
                orgs = await db.list_organizations()
                org_id = random.choice(orgs)["id"] if orgs else None
                await project_manager.auto_generate_project(org_id)
                self.stats["auto_projects"] += 1
        except Exception as e:
            logger.debug("Auto project error: %s", e)

        try:
            running_exps = await db.list_experiments(status="running")
            for exp in running_exps[:2]:
                if random.random() > 0.6:
                    await experiment_engine.complete_experiment(exp["id"])
                    self.stats["auto_experiments"] += 1
        except Exception as e:
            logger.debug("Auto experiment error: %s", e)

        try:
            submitted_pubs = await db.list_publications(status="submitted")
            for pub in submitted_pubs[:2]:
                if random.random() > 0.5:
                    await publication_engine.publish(pub["id"])
                    self.stats["auto_publications"] += 1
        except Exception as e:
            logger.debug("Auto publish error: %s", e)

        try:
            unlocked_techs = await db.list_technologies(status="unlocked")
            if unlocked_techs and random.random() > 0.7:
                tech = random.choice(unlocked_techs)
                await technology_tree_engine.contribute_research(
                    tech["id"], "system", points=random.randint(5, 15)
                )
                self.stats["tech_contributions"] += 1
        except Exception as e:
            logger.debug("Auto tech contribution error: %s", e)

        try:
            if random.random() > 0.8:
                await research_innovation_engine.generate_idea()
        except Exception as e:
            logger.debug("Auto innovation error: %s", e)

        await dispatch(Event(EventType.RESEARCH_TICK if hasattr(EventType, 'RESEARCH_TICK') else EventType.SIMULATION_TICK, {
            "tick": self.stats["total_ticks"],
            "stats": self.stats.copy(),
        }))

        elapsed = time.monotonic() - start
        logger.debug("Research tick %d completed in %.1fs", self.stats["total_ticks"], elapsed)

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "tick_interval": self.tick_interval,
            "stats": self.stats.copy(),
            "organizations": organization_manager.get_state(),
            "projects": project_manager.get_state(),
            "knowledge_graph": knowledge_graph_engine.get_state(),
            "experiments": experiment_engine.get_state(),
            "publications": publication_engine.get_state(),
            "peer_review": peer_review_engine.get_state(),
            "technology": technology_tree_engine.get_state(),
            "diffusion": knowledge_diffusion_engine.get_state(),
            "funding": funding_engine.get_state(),
            "innovation": research_innovation_engine.get_state(),
            "intelligence": research_intelligence.get_state(),
        }

    def set_speed(self, interval: int):
        self.tick_interval = max(10, min(300, interval))
        logger.info("Research tick interval set to %ds", self.tick_interval)


import random  # noqa: E402


research_engine = ResearchEngine()
