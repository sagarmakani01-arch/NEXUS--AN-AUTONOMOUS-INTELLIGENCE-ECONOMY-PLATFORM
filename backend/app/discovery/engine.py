import asyncio
import json
import logging
import random

from app.core.event_bus import Event, EventType, dispatch
from app.discovery import persistence as db
from app.discovery.archive import archive_experiment, archive_hypothesis, archive_pattern
from app.discovery.auto_experiment import generate_experiment as auto_gen_experiment
from app.discovery.experiment_framework import create_controlled_experiment, run_experiment, compare_experiments
from app.discovery.hypothesis_generator import generate_hypothesis_from_pattern
from app.discovery.knowledge_graph import (
    add_discovery_node,
    add_relationship,
    get_knowledge_graph,
    link_experiment_to_knowledge,
    link_hypothesis_to_knowledge,
    link_pattern_to_knowledge,
)
from app.discovery.laboratory import auto_run_labs, initialize_laboratories
from app.discovery.pattern_discovery import discover_patterns
from app.discovery.report_generator import generate_report
from app.discovery.research_agents import agent_tick, assign_agents_to_labs, initialize_agents
from app.discovery.validation import validate_hypothesis

logger = logging.getLogger("nexus.discovery.engine")


DISCOVERY_EVENTS = [
    "ExperimentStarted",
    "ExperimentCompleted",
    "PatternDetected",
    "HypothesisGenerated",
    "DiscoveryRecorded",
    "ReportCreated",
]


class DiscoveryEngine:
    def __init__(self):
        self.running = False
        self.stats = {
            "total_ticks": 0,
            "experiments_created": 0,
            "patterns_discovered": 0,
            "hypotheses_generated": 0,
            "reports_created": 0,
            "archives_stored": 0,
        }
        self._initialized = False

    async def start(self):
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize()
        logger.info("Discovery engine started")

    async def _initialize(self):
        try:
            await initialize_laboratories()
            await initialize_agents()
            await assign_agents_to_labs()
            self._initialized = True
            logger.info("Discovery engine initialized")
        except Exception as exc:
            logger.error("discovery_init_error: %s", exc)

    async def stop(self):
        self.running = False
        logger.info("Discovery engine stopped")

    async def tick(self, full_state: dict | None = None):
        if not self.running:
            return
        self.stats["total_ticks"] += 1

        try:
            await self._discovery_cycle(full_state)
        except Exception as exc:
            logger.error("discovery_tick_error: %s", exc)

    async def _discovery_cycle(self, full_state: dict | None = None):
        tick = self.stats["total_ticks"]

        if tick % 5 == 0 or (full_state and random.random() < 0.1):
            await self._auto_experiment_cycle()

        if tick % 10 == 0 or (full_state and random.random() < 0.15):
            await self._pattern_discovery_cycle()

        if tick % 15 == 0:
            await self._hypothesis_cycle()

        if tick % 8 == 0:
            await self._lab_cycle()

        if tick % 7 == 0:
            await self._agent_cycle()

        if tick % 20 == 0:
            await self._archive_cycle()

    async def _auto_experiment_cycle(self):
        try:
            snapshots = await db.get_snapshots(limit=50)
            if snapshots:
                exp = await auto_gen_experiment()
                if exp:
                    self.stats["experiments_created"] += 1
                    node = await link_experiment_to_knowledge(exp.get("id", ""), exp.get("title", ""), exp.get("result_summary"))
                    await dispatch(Event(EventType.EXPERIMENT_COMPLETED, {
                        "experiment_id": exp.get("id"),
                        "title": exp.get("title"),
                        "confidence": exp.get("confidence_score", 0),
                    }))
        except Exception as exc:
            logger.error("auto_experiment_error: %s", exc)

    async def _pattern_discovery_cycle(self):
        try:
            snapshots = await db.get_snapshots(limit=100)
            if len(snapshots) >= 10:
                patterns = await discover_patterns(snapshots)
                for pattern in patterns:
                    self.stats["patterns_discovered"] += 1
                    node = await link_pattern_to_knowledge(pattern.get("id", ""), pattern.get("title", ""), pattern.get("confidence", 0.5))
                    await dispatch(Event(EventType.PATTERN_DISCOVERED, {
                        "pattern_id": pattern.get("id"),
                        "title": pattern.get("title"),
                        "confidence": pattern.get("confidence", 0),
                    }))
        except Exception as exc:
            logger.error("pattern_discovery_error: %s", exc)

    async def _hypothesis_cycle(self):
        try:
            patterns = await db.list_patterns(min_confidence=0.3, limit=5)
            for pattern in patterns:
                if random.random() < 0.3:
                    hypothesis = await generate_hypothesis_from_pattern(pattern["id"])
                    if hypothesis:
                        self.stats["hypotheses_generated"] += 1
                        node = await link_hypothesis_to_knowledge(hypothesis.get("id", ""), hypothesis.get("title", ""), hypothesis.get("confidence_level", 0.5))
                        await dispatch(Event(EventType.DISCOVERY_MADE, {
                            "hypothesis_id": hypothesis.get("id"),
                            "title": hypothesis.get("title"),
                            "confidence": hypothesis.get("confidence_level", 0),
                        }))
                        validated = await validate_hypothesis(hypothesis["id"])
                        if validated:
                            await dispatch(Event(EventType.DISCOVERY_MADE, {
                                "hypothesis_id": hypothesis["id"],
                                "status": "validated",
                                "new_confidence": validated.get("confidence_level", 0),
                            }))
        except Exception as exc:
            logger.error("hypothesis_cycle_error: %s", exc)

    async def _lab_cycle(self):
        try:
            results = await auto_run_labs()
            for result in results:
                self.stats["experiments_created"] += 1
        except Exception as exc:
            logger.error("lab_cycle_error: %s", exc)

    async def _agent_cycle(self):
        try:
            results = await agent_tick()
        except Exception as exc:
            logger.error("agent_cycle_error: %s", exc)

    async def _archive_cycle(self):
        try:
            experiments = await db.list_experiments(status="completed", limit=5)
            for exp in experiments:
                await archive_experiment(exp["id"])
                self.stats["archives_stored"] += 1
            hypotheses = await db.list_hypotheses(status="validated", limit=5)
            for hyp in hypotheses:
                await archive_hypothesis(hyp["id"])
                self.stats["archives_stored"] += 1
            patterns = await db.list_patterns(limit=5)
            for pat in patterns:
                await archive_pattern(pat["id"])
                self.stats["archives_stored"] += 1
        except Exception as exc:
            logger.error("archive_cycle_error: %s", exc)

    async def get_full_state(self) -> dict:
        try:
            stats = await db.get_discovery_stats()
        except Exception:
            stats = {}
        return {
            "initialized": self._initialized,
            "running": self.running,
            "stats": self.stats,
            "db_stats": stats,
            "events": DISCOVERY_EVENTS,
        }

    async def run_manual_experiment(
        self, title: str, research_question: str, hypothesis: str,
        variables: dict | None = None, duration: int = 100
    ) -> dict:
        exp = await create_controlled_experiment(
            title=title,
            research_question=research_question,
            hypothesis=hypothesis,
            variables=variables,
            duration_ticks=duration,
        )
        result = await run_experiment(exp["id"])
        if result:
            await link_experiment_to_knowledge(result["id"], result["title"], result.get("result_summary"))
            node = await link_experiment_to_knowledge(result["id"], result["title"], result.get("result_summary"))
            await dispatch(Event(EventType.EXPERIMENT_COMPLETED, {
                "experiment_id": result["id"],
                "title": result["title"],
                "confidence": result.get("confidence_score", 0),
            }))
            report = await generate_report(experiment_id=result["id"])
            if report:
                self.stats["reports_created"] += 1
                await dispatch(Event(EventType.DISCOVERY_MADE, {
                    "type": "report",
                    "report_id": report.get("id"),
                    "title": report.get("title"),
                }))
            self.stats["experiments_created"] += 1
        return exp if result is None else result


discovery_engine = DiscoveryEngine()
