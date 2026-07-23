import asyncio
import logging

from app.economy.market_engine import market_engine
from app.economy.pricing import pricing_engine
from app.economy.resource_economy import resource_economy
from app.economy.finance import finance_engine
from app.economy.investment import investment_engine
from app.economy.events import economic_events
from app.economy.wealth import wealth_distribution
from app.economy.intelligence import economic_intelligence
from app.economy import persistence as eco_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.economy.engine")


class EconomyEngine:
    def __init__(self):
        self.running = False
        self._task: asyncio.Task | None = None
        self._tick_interval = 30.0
        self.markets = market_engine
        self.pricing = pricing_engine
        self.resources = resource_economy
        self.finance = finance_engine
        self.investments = investment_engine
        self.events = economic_events
        self.wealth = wealth_distribution
        self.intelligence = economic_intelligence
        self.stats = {
            "total_ticks": 0,
            "economic_events": 0,
            "price_adjustments": 0,
        }
        self._initialized = False

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize_economy()
            self._initialized = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("economy_engine_started")

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("economy_engine_stopped")

    async def _initialize_economy(self) -> None:
        try:
            from app.simulation.engine import engine as sim_engine
            agent_count = len(sim_engine.agents) if sim_engine.agents else 100
            company_count = 0
            try:
                from app.organization.persistence import list_companies
                companies = await list_companies()
                company_count = len(companies)
            except Exception:
                pass

            await self.markets.initialize_default_markets()
            await self.resources.initialize(agent_count)
            await self.markets.update_market_activity(agent_count, company_count)
            await self.markets.update_prices()
            await self.wealth.analyze()
            logger.info("economy_initialized agents=%d companies=%d", agent_count, company_count)
        except Exception as exc:
            logger.error("economy_init_error: %s", exc)

    async def _run_loop(self) -> None:
        try:
            while self.running:
                await self._tick()
                await asyncio.sleep(self._tick_interval)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("economy_loop_error: %s", exc)
            self.running = False

    async def _tick(self) -> None:
        self.stats["total_ticks"] += 1
        try:
            from app.simulation.engine import engine as sim_engine
            agent_count = len(sim_engine.agents) if sim_engine.agents else 100
            company_count = 0
            try:
                from app.organization.persistence import list_companies
                companies = await list_companies()
                company_count = len(companies)
            except Exception:
                pass

            await self.markets.update_market_activity(agent_count, company_count)
            await self.markets.update_prices()
            self.resources.update_prices()
            self.finance.update_rates(1.0)

            if self.stats["total_ticks"] % 5 == 0:
                await self.wealth.analyze()

            if self.stats["total_ticks"] % 10 == 0:
                gdp = await self._calculate_gdp()
                await eco_db.record_indicator("gdp", gdp)
                wealth_stats = await wealth_distribution.analyze()
                await eco_db.record_indicator(
                    "gini_coefficient",
                    wealth_stats.get("gini_coefficient", 0),
                )

            event_result = await self.events.maybe_generate_event(self.stats["total_ticks"])
            if event_result:
                self.stats["economic_events"] += 1

            self.stats["price_adjustments"] = self.pricing.stats.get("calculations", 0)

        except Exception as exc:
            logger.error("economy_tick_error: %s", exc)

    async def _calculate_gdp(self) -> float:
        try:
            from app.resources.persistence import get_all_wallets
            wallets = await get_all_wallets()
            total_balance = sum(w.get("balance", 0) for w in wallets)
            markets = await self.markets.get_all_markets()
            total_volume = sum(m["volume"] for m in markets)
            return round(total_balance + total_volume * 10, 2)
        except Exception:
            return 0.0

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "stats": self.stats.copy(),
            "tick_interval": self._tick_interval,
            "markets": self.markets.get_state(),
            "pricing": self.pricing.get_state(),
            "resources": self.resources.get_state(),
            "finance": self.finance.get_state(),
            "investments": self.investments.get_state(),
            "events": self.events.get_state(),
            "wealth": self.wealth.get_state(),
            "intelligence": self.intelligence.get_state(),
        }


economy_engine = EconomyEngine()
