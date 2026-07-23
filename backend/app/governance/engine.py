import asyncio
import logging

from app.governance.authority import authority_system
from app.governance.laws import law_engine
from app.governance.policies import policy_engine
from app.governance.taxation import taxation_system
from app.governance.regulation import regulation_system
from app.governance.conflict import conflict_resolution
from app.governance.voting import voting_system
from app.governance.intelligence import governance_intelligence
from app.governance import persistence as gov_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.engine")


class GovernanceEngine:
    def __init__(self):
        self.running = False
        self._task: asyncio.Task | None = None
        self._tick_interval = 60.0
        self.authority = authority_system
        self.laws = law_engine
        self.policies = policy_engine
        self.taxation = taxation_system
        self.regulation = regulation_system
        self.conflicts = conflict_resolution
        self.voting = voting_system
        self.intelligence = governance_intelligence
        self.stats = {
            "total_ticks": 0,
            "actions_taken": 0,
        }
        self._initialized = False

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize_governance()
            self._initialized = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("governance_engine_started")

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("governance_engine_stopped")

    async def _initialize_governance(self) -> None:
        try:
            existing = await self.authority.list_entities()
            if existing:
                return

            gov = await self.authority.create_entity(
                name="NEXUS Global Administration",
                entity_type="government",
                description="Global governing body for the NEXUS civilization",
                authority_level="government",
            )

            await self.laws.create_law(
                name="Fair Labor Standards",
                description="Ensures fair treatment and compensation for all workers",
                creator_id=gov["entity_id"],
                category="labor", severity="high",
            )
            await self.laws.create_law(
                name="Market Fairness Act",
                description="Prevents market manipulation and ensures fair competition",
                creator_id=gov["entity_id"],
                category="economic", severity="high",
            )
            await self.laws.create_law(
                name="Data Protection Regulation",
                description="Protects agent data and knowledge from unauthorized access",
                creator_id=gov["entity_id"],
                category="technology", severity="medium",
            )

            await self.policies.create_policy(
                name="Economic Growth Initiative",
                description="Promotes investment and innovation in the economy",
                policy_type="economic", creator_id=gov["entity_id"],
                rules={"investment_incentive": 0.05, "innovation_bonus": 10},
                expected_outcome="10% GDP growth over 30 days",
                duration_days=30,
            )
            await self.policies.create_policy(
                name="Resource Sustainability Policy",
                description="Ensures sustainable use of scarce resources",
                policy_type="resource", creator_id=gov["entity_id"],
                rules={"max_consumption_ratio": 0.8, "renewal_priority": True},
                expected_outcome="Maintain resource levels above scarcity threshold",
                duration_days=60,
            )

            await self.taxation.create_tax(
                name="Income Tax", tax_type="income",
                rate=0.05, target="agent",
                creator_id=gov["entity_id"],
                description="Tax on agent earnings",
                revenue_use="public_services",
            )
            await self.taxation.create_tax(
                name="Corporate Tax", tax_type="company",
                rate=0.08, target="company",
                creator_id=gov["entity_id"],
                description="Tax on company revenue",
                revenue_use="infrastructure",
            )
            await self.taxation.create_tax(
                name="Transaction Tax", tax_type="transaction",
                rate=0.02, target="transaction",
                creator_id=gov["entity_id"],
                description="Tax on financial transactions",
                revenue_use="expansion",
            )

            await self.regulation.create_regulation(
                name="Licensing Requirement",
                description="Companies must obtain license to operate",
                regulation_type="licensing",
                authority_id=gov["entity_id"],
                target_sector="all",
                requirements={"license_type": "business", "renewal_days": 90},
                max_violations=3,
                penalty_description="License revocation and fine",
            )

            logger.info("governance_initialized")
        except Exception as exc:
            logger.error("governance_init_error: %s", exc)

    async def _run_loop(self) -> None:
        try:
            while self.running:
                await self._tick()
                await asyncio.sleep(self._tick_interval)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("governance_loop_error: %s", exc)
            self.running = False

    async def _tick(self) -> None:
        self.stats["total_ticks"] += 1
        try:
            await self.policies.check_expired_policies()

            if self.stats["total_ticks"] % 10 == 0:
                await self._auto_resolve_conflicts()

            if self.stats["total_ticks"] % 5 == 0:
                await self._maybe_collect_taxes()

        except Exception as exc:
            logger.error("governance_tick_error: %s", exc)

    async def _auto_resolve_conflicts(self) -> None:
        open_conflicts = await self.conflicts.get_open_conflicts()
        for conflict in open_conflicts[:2]:
            if conflict.get("resolution_method") == "negotiation":
                result = await self.conflicts.resolve_negotiation(conflict["id"])
                if result.get("success"):
                    self.stats["actions_taken"] += 1
            elif conflict.get("resolution_method") == "arbitration":
                result = await self.conflicts.resolve_arbitration(conflict["id"])
                if result.get("success"):
                    self.stats["actions_taken"] += 1

    async def _maybe_collect_taxes(self) -> None:
        try:
            from app.simulation.engine import engine as sim_engine
            if not sim_engine.agents:
                return
            import random
            agent = random.choice(sim_engine.agents)
            from app.resources.persistence import get_wallet
            wallet = await get_wallet(agent.id)
            if wallet and wallet.get("balance", 0) > 50:
                income = wallet.get("balance", 0) * 0.1
                await self.taxation.collect_tax(agent.id, income)
                self.stats["actions_taken"] += 1
        except Exception:
            pass

    async def get_agent_governance_state(self, agent_id: str) -> dict:
        from app.governance.persistence import list_conflicts
        agent_conflicts = await list_conflicts(party_id=agent_id)
        return {
            "conflicts": agent_conflicts,
            "is_in_conflict": len([c for c in agent_conflicts if c.get("status") == "open"]) > 0,
        }

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "stats": self.stats.copy(),
            "tick_interval": self._tick_interval,
            "authority": self.authority.get_state(),
            "laws": self.laws.get_state(),
            "policies": self.policies.get_state(),
            "taxation": self.taxation.get_state(),
            "regulation": self.regulation.get_state(),
            "conflicts": self.conflicts.get_state(),
            "voting": self.voting.get_state(),
            "intelligence": self.intelligence.get_state(),
        }


governance_engine = GovernanceEngine()
