import logging
import random

from app.economy import persistence as eco_db
from app.economy.market_engine import market_engine
from app.economy.resource_economy import resource_economy, RESOURCE_TYPES
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.economy.events")

EVENT_TYPES = [
    "market_growth", "market_crash", "resource_shortage",
    "new_industry", "company_failure", "economic_boom",
    "economic_recession", "innovation_breakthrough",
    "regulation_change", "trade_disruption",
]


class EconomicEventGenerator:
    def __init__(self):
        self.stats = {
            "events_generated": 0,
            "booms": 0,
            "recessions": 0,
            "shortages": 0,
        }

    async def maybe_generate_event(self, tick_count: int) -> dict | None:
        if random.random() > 0.08:
            return None

        event_type = random.choice(EVENT_TYPES)
        return await self._generate_event(event_type)

    async def _generate_event(self, event_type: str) -> dict | None:
        generators = {
            "market_growth": self._gen_market_growth,
            "market_crash": self._gen_market_crash,
            "resource_shortage": self._gen_resource_shortage,
            "economic_boom": self._gen_economic_boom,
            "economic_recession": self._gen_economic_recession,
            "innovation_breakthrough": self._gen_innovation,
            "company_failure": self._gen_company_failure,
            "new_industry": self._gen_new_industry,
            "regulation_change": self._gen_regulation,
            "trade_disruption": self._gen_trade_disruption,
        }
        gen = generators.get(event_type)
        if not gen:
            return None
        return await gen()

    async def _gen_market_growth(self) -> dict:
        markets = await market_engine.get_all_markets()
        if not markets:
            return None
        market = random.choice(markets)
        growth = random.uniform(0.1, 0.3)
        new_price = market["current_price"] * (1 + growth)
        await eco_db.update_market(market["id"], current_price=round(new_price, 2))
        event_id = await eco_db.record_economic_event(
            "market_growth",
            f"Boom in {market['name']}",
            f"Strong demand drives {market['name']} prices up {growth:.0%}",
            "medium", [market["id"]], [market["market_type"]], growth,
        )
        self.stats["events_generated"] += 1
        self.stats["booms"] += 1
        return {"event_id": event_id, "type": "market_growth", "market": market["name"]}

    async def _gen_market_crash(self) -> dict:
        markets = await market_engine.get_all_markets()
        if not markets:
            return None
        market = random.choice(markets)
        crash = random.uniform(0.15, 0.40)
        new_price = market["current_price"] * (1 - crash)
        await eco_db.update_market(market["id"], current_price=round(new_price, 2))
        event_id = await eco_db.record_economic_event(
            "market_crash",
            f"Crash in {market['name']}",
            f"Market panic causes {market['name']} to drop {crash:.0%}",
            "high", [market["id"]], [market["market_type"]], -crash,
        )
        self.stats["events_generated"] += 1
        self.stats["recessions"] += 1
        return {"event_id": event_id, "type": "market_crash", "market": market["name"]}

    async def _gen_resource_shortage(self) -> dict:
        rtype = random.choice(list(RESOURCE_TYPES.keys()))
        config = RESOURCE_TYPES[rtype]
        resource_economy.global_supply[rtype] = int(config["scarcity_threshold"] * 0.3)
        resource_economy._update_scarcity(rtype)
        event_id = await eco_db.record_economic_event(
            "resource_shortage",
            f"Shortage of {config['name']}",
            f"Critical shortage: {config['name']} supply dropped to dangerous levels",
            "high", [], [], -0.3,
        )
        self.stats["events_generated"] += 1
        self.stats["shortages"] += 1
        return {"event_id": event_id, "type": "resource_shortage", "resource": config["name"]}

    async def _gen_economic_boom(self) -> dict:
        for rtype in RESOURCE_TYPES:
            resource_economy.global_supply[rtype] = int(resource_economy.global_supply[rtype] * 1.3)
        event_id = await eco_db.record_economic_event(
            "economic_boom",
            "Economic Boom",
            "Strong economic growth across all sectors",
            "low", [], [], 0.2,
        )
        self.stats["events_generated"] += 1
        self.stats["booms"] += 1
        return {"event_id": event_id, "type": "economic_boom"}

    async def _gen_economic_recession(self) -> dict:
        for rtype in RESOURCE_TYPES:
            resource_economy.global_supply[rtype] = int(resource_economy.global_supply[rtype] * 0.7)
        markets = await market_engine.get_all_markets()
        for market in markets:
            drop = random.uniform(0.05, 0.15)
            new_price = market["current_price"] * (1 - drop)
            await eco_db.update_market(market["id"], current_price=round(new_price, 2))
        event_id = await eco_db.record_economic_event(
            "economic_recession",
            "Economic Recession",
            "Broad economic downturn affecting all sectors",
            "high", [], [], -0.2,
        )
        self.stats["events_generated"] += 1
        self.stats["recessions"] += 1
        return {"event_id": event_id, "type": "economic_recession"}

    async def _gen_innovation(self) -> dict:
        event_id = await eco_db.record_economic_event(
            "innovation_breakthrough",
            "Innovation Breakthrough",
            "New technology or process creates market opportunities",
            "medium", [], [], 0.15,
        )
        self.stats["events_generated"] += 1
        return {"event_id": event_id, "type": "innovation_breakthrough"}

    async def _gen_company_failure(self) -> dict:
        event_id = await eco_db.record_economic_event(
            "company_failure",
            "Company Bankruptcy",
            "A company has failed due to financial difficulties",
            "medium", [], [], -0.1,
        )
        self.stats["events_generated"] += 1
        return {"event_id": event_id, "type": "company_failure"}

    async def _gen_new_industry(self) -> dict:
        event_id = await eco_db.record_economic_event(
            "new_industry",
            "New Industry Emerges",
            "A new market sector emerges with growth potential",
            "low", [], [], 0.1,
        )
        self.stats["events_generated"] += 1
        return {"event_id": event_id, "type": "new_industry"}

    async def _gen_regulation(self) -> dict:
        event_id = await eco_db.record_economic_event(
            "regulation_change",
            "Regulation Change",
            "New economic regulations affect market conditions",
            "medium", [], [], random.uniform(-0.05, 0.05),
        )
        self.stats["events_generated"] += 1
        return {"event_id": event_id, "type": "regulation_change"}

    async def _gen_trade_disruption(self) -> dict:
        event_id = await eco_db.record_economic_event(
            "trade_disruption",
            "Trade Disruption",
            "Supply chain issues disrupt normal economic activity",
            "medium", [], [], -0.08,
        )
        self.stats["events_generated"] += 1
        return {"event_id": event_id, "type": "trade_disruption"}

    def get_state(self) -> dict:
        return {"stats": self.stats.copy(), "event_types": EVENT_TYPES}


economic_events = EconomicEventGenerator()
