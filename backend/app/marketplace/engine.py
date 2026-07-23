from __future__ import annotations

import asyncio
import logging
import random
import time

from app.marketplace.bidding import bidding_engine
from app.marketplace.contracts import contract_manager
from app.marketplace.matching import matching_engine
from app.marketplace.negotiation import negotiation_engine
from app.marketplace.persistence import get_marketplace_stats
from app.marketplace.task_manager import task_manager

logger = logging.getLogger("nexus.marketplace.engine")


class MarketplaceEngine:
    def __init__(self) -> None:
        self._running = False
        self._task: asyncio.Task | None = None
        self._tick_interval = 30.0
        self._last_tick = 0.0
        self._stats = {
            "tasks_created": 0,
            "proposals_submitted": 0,
            "contracts_completed": 0,
            "total_volume": 0,
        }

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("marketplace_engine_started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("marketplace_engine_stopped")

    async def _run_loop(self) -> None:
        try:
            while self._running:
                await self._tick()
                await asyncio.sleep(self._tick_interval)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("marketplace_loop_error: %s", exc)

    async def _tick(self) -> None:
        self._last_tick = time.time()
        try:
            await self._ensure_marketplace_tasks()
            await self._process_idle_agents()
        except Exception as exc:
            logger.error("marketplace_tick_error: %s", exc)

    async def _ensure_marketplace_tasks(self) -> None:
        stats = await get_marketplace_stats()
        open_tasks = stats.get("tasks", {}).get("open", 0)
        if open_tasks < 5:
            count = 5 - open_tasks
            created = await task_manager.generate_marketplace_tasks(count)
            self._stats["tasks_created"] += len(created)
            logger.info("marketplace_tasks_replenished count=%d", len(created))

    async def _process_idle_agents(self) -> None:
        from app.simulation.engine import engine as sim_engine
        idle_agents = [a for a in sim_engine.agents if a.current_status == "idle"]
        if not idle_agents:
            return

        sample_size = min(len(idle_agents), 10)
        sampled = random.sample(idle_agents, sample_size)

        for agent in sampled:
            if random.random() > 0.3:
                continue
            profile = sim_engine.profiles.get(agent.id)
            if not profile:
                continue
            agent_skills = [s.get("skill_name", "") for s in profile.skills]
            opportunities = await matching_engine.find_opportunities(
                agent_skills, agent.reputation, agent.energy, limit=3,
            )
            if opportunities:
                task = random.choice(opportunities)
                proposed = round(task.get("reward", 50) * random.uniform(0.8, 1.1), 2)
                await bidding_engine.submit_proposal(
                    task_id=task["id"], agent_id=agent.id,
                    proposed_reward=proposed,
                    cover_letter=f"Proposal from {agent.name}",
                    estimated_duration=f"{random.randint(2, 24)}h",
                )
                self._stats["proposals_submitted"] += 1

    async def create_task_from_poster(
        self, poster_id: str, title: str, description: str = "",
        required_skills: list[str] | None = None, reward: float = 0,
        priority: str = "medium", deadline: str | None = None,
    ) -> dict:
        task = await task_manager.create_task(
            poster_id=poster_id, title=title, description=description,
            required_skills=required_skills, reward=reward,
            priority=priority, deadline=deadline,
        )
        self._stats["tasks_created"] += 1
        return task

    async def submit_proposal(
        self, task_id: str, agent_id: str, proposed_reward: float,
        cover_letter: str = "", estimated_duration: str = "",
    ) -> dict:
        result = await bidding_engine.submit_proposal(
            task_id=task_id, agent_id=agent_id, proposed_reward=proposed_reward,
            cover_letter=cover_letter, estimated_duration=estimated_duration,
        )
        if "error" not in result:
            self._stats["proposals_submitted"] += 1
        return result

    async def accept_proposal_and_create_contract(self, proposal_id: str) -> dict:
        proposal_result = await bidding_engine.accept_proposal(proposal_id)
        if "error" in proposal_result:
            return proposal_result

        from app.marketplace.persistence import get_proposal
        proposal = await get_proposal(proposal_id)
        if not proposal:
            return {"error": "Proposal not found after acceptance"}

        task = await task_manager.get_task(proposal["task_id"])
        contract = await contract_manager.create_contract(
            task_id=proposal["task_id"],
            proposal_id=proposal_id,
            poster_id=task["posted_by"] if task else "unknown",
            agent_id=proposal["agent_id"],
            agreed_reward=proposal["proposed_reward"],
        )
        return contract

    async def complete_contract(
        self, contract_id: str, result: str = "", rating: float = 5.0, feedback: str = "",
    ) -> dict:
        contract = await contract_manager.complete_contract(
            contract_id, result=result, rating=rating, feedback=feedback,
        )
        if "error" not in contract:
            self._stats["contracts_completed"] += 1
            self._stats["total_volume"] += contract.get("agreed_reward", 0)

            from app.resources.manager import resource_manager
            await resource_manager.on_work_completed(
                contract["agent_id"], contract["agreed_reward"],
                f"Contract: {contract.get('task_id', '')}",
            )
        return contract

    async def get_full_state(self) -> dict:
        stats = await get_marketplace_stats()
        return {
            **stats,
            "engine_stats": self._stats,
            "running": self._running,
        }

    def get_state(self) -> dict:
        return {
            "running": self._running,
            "stats": self._stats,
            "tick_interval": self._tick_interval,
        }


marketplace_engine = MarketplaceEngine()
