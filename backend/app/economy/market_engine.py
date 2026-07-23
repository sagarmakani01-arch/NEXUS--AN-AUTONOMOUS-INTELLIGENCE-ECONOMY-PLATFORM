import logging
import random

from app.economy import persistence as eco_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.economy.markets")

MARKET_TYPES = [
    "labor", "skill", "technology", "knowledge", "service", "asset",
]

DEFAULT_MARKETS = [
    ("AI Engineers Labor", "labor", "Market for AI and ML engineers", 150.0),
    ("Software Developers Labor", "labor", "Market for software developers", 120.0),
    ("Data Scientists Labor", "labor", "Market for data science talent", 140.0),
    ("Project Managers Labor", "labor", "Market for project management", 110.0),
    ("Cybersecurity Experts Labor", "labor", "Market for security specialists", 160.0),
    ("Python Skill", "skill", "Python programming expertise", 50.0),
    ("Machine Learning Skill", "skill", "ML model development", 80.0),
    ("Cloud Architecture Skill", "skill", "Cloud infrastructure design", 70.0),
    ("DevOps Skill", "skill", "CI/CD and operations", 60.0),
    ("Blockchain Skill", "skill", "Blockchain development", 90.0),
    ("Cloud Computing Technology", "technology", "Cloud services and infrastructure", 200.0),
    ("AI Platform Technology", "technology", "AI/ML platforms and tools", 250.0),
    ("Cybersecurity Tech", "technology", "Security solutions", 180.0),
    ("Data Analytics Tech", "technology", "Analytics platforms", 160.0),
    ("Blockchain Tech", "technology", "Distributed ledger technology", 220.0),
    ("Technical Documentation", "knowledge", "Technical writing and docs", 40.0),
    ("Research Papers", "knowledge", "Academic and industry research", 60.0),
    ("Market Analysis", "knowledge", "Market intelligence reports", 70.0),
    ("Legal Knowledge", "knowledge", "Legal expertise and compliance", 80.0),
    ("Financial Knowledge", "knowledge", "Financial analysis and planning", 75.0),
    ("Consulting Service", "service", "Business consulting services", 100.0),
    ("Design Service", "service", "UI/UX and graphic design", 90.0),
    ("Marketing Service", "service", "Digital marketing and advertising", 85.0),
    ("Accounting Service", "service", "Financial accounting services", 95.0),
    ("Legal Service", "service", "Legal representation and advice", 110.0),
    ("Digital Assets", "asset", "Digital goods and licenses", 50.0),
    ("Compute Resources", "asset", "Computing power and storage", 120.0),
    ("Intellectual Property", "asset", "Patents and IP rights", 300.0),
    ("Company Shares", "asset", "Equity in companies", 200.0),
    ("Research Data", "asset", "Datasets and training data", 150.0),
]


class MarketEngine:
    def __init__(self):
        self.stats = {
            "markets_created": 0,
            "price_updates": 0,
            "trades_executed": 0,
        }

    async def initialize_default_markets(self) -> int:
        existing = await eco_db.list_markets()
        if existing:
            return 0
        count = 0
        for name, mtype, desc, base_price in DEFAULT_MARKETS:
            await eco_db.create_market(name, mtype, desc, base_price)
            count += 1
        self.stats["markets_created"] = count
        logger.info("initialized_default_markets count=%d", count)
        return count

    async def update_prices(self) -> None:
        markets = await eco_db.list_markets()
        for market in markets:
            supply = market["supply"]
            demand = market["demand"]
            current_price = market["current_price"]
            base_price = market["base_price"]
            volatility = market["volatility"]

            if supply == 0 and demand == 0:
                supply = random.randint(10, 100)
                demand = random.randint(10, 100)

            if demand > supply:
                scarcity = min(2.0, demand / max(supply, 1))
                price_change = scarcity * 0.05 * current_price
            elif supply > demand:
                surplus = min(2.0, supply / max(demand, 1))
                price_change = -surplus * 0.03 * current_price
            else:
                price_change = 0.0

            noise = random.gauss(0, volatility * 0.01 * current_price) if volatility > 0 else 0
            new_price = current_price + price_change + noise
            new_price = max(base_price * 0.1, min(base_price * 5.0, new_price))

            change_pct = ((new_price - current_price) / current_price * 100) if current_price > 0 else 0

            new_growth = (new_price - base_price) / base_price if base_price > 0 else 0

            await eco_db.update_market(
                market["id"],
                current_price=round(new_price, 2),
                supply=supply,
                demand=demand,
                growth_rate=round(new_growth, 4),
            )
            await eco_db.record_price_history(
                market["id"], round(new_price, 2),
                supply, demand, market["volume"],
                round(change_pct, 2),
            )
            self.stats["price_updates"] += 1

    async def update_market_activity(self, agent_count: int, company_count: int) -> None:
        markets = await eco_db.list_markets()
        for market in markets:
            mtype = market["market_type"]
            if mtype == "labor":
                base_supply = agent_count
                base_demand = company_count * 3
            elif mtype == "skill":
                base_supply = agent_count // 2
                base_demand = company_count * 2
            elif mtype == "technology":
                base_supply = company_count
                base_demand = agent_count
            elif mtype == "knowledge":
                base_supply = agent_count // 3
                base_demand = company_count * 2
            elif mtype == "service":
                base_supply = agent_count // 2
                base_demand = company_count
            else:
                base_supply = company_count
                base_demand = agent_count

            noise_s = random.randint(-base_supply // 4, base_supply // 4) if base_supply > 4 else 0
            noise_d = random.randint(-base_demand // 4, base_demand // 4) if base_demand > 4 else 0
            supply = max(1, base_supply + noise_s)
            demand = max(1, base_demand + noise_d)

            volume = market["volume"] + random.randint(1, 5)
            await eco_db.update_market(market["id"], supply=supply, demand=demand, volume=volume)

    async def get_market_data(self, market_id: str) -> dict | None:
        market = await eco_db.get_market(market_id)
        if not market:
            return None
        history = await eco_db.get_price_history(market_id, limit=20)
        market["price_history"] = history
        return market

    async def get_all_markets(self, market_type: str | None = None) -> list[dict]:
        return await eco_db.list_markets(market_type)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy(), "market_types": MARKET_TYPES}


market_engine = MarketEngine()
