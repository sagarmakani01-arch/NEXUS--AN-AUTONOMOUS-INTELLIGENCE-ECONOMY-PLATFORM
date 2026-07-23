import logging

from app.economy import persistence as eco_db
from app.economy.market_engine import market_engine
from app.economy.resource_economy import resource_economy
from app.economy.finance import finance_engine
from app.economy.wealth import wealth_distribution

logger = logging.getLogger("nexus.economy.intelligence")


class EconomicIntelligence:
    def __init__(self):
        self.stats = {"queries": 0}

    async def get_market_trends(self) -> dict:
        markets = await market_engine.get_all_markets()
        trends = {}
        for market in markets:
            history = await eco_db.get_price_history(market["id"], limit=5)
            if len(history) >= 2:
                recent = history[0]["price"]
                older = history[-1]["price"]
                trend_pct = ((recent - older) / older * 100) if older > 0 else 0
            else:
                trend_pct = 0.0
            trends[market["name"]] = {
                "market_type": market["market_type"],
                "current_price": market["current_price"],
                "trend_pct": round(trend_pct, 2),
                "supply": market["supply"],
                "demand": market["demand"],
                "growth_rate": market["growth_rate"],
            }
        self.stats["queries"] += 1
        return trends

    async def get_price_changes(self) -> list[dict]:
        markets = await market_engine.get_all_markets()
        changes = []
        for market in markets:
            history = await eco_db.get_price_history(market["id"], limit=2)
            if len(history) >= 2:
                change = history[0]["price"] - history[1]["price"]
                change_pct = (change / history[1]["price"] * 100) if history[1]["price"] > 0 else 0
                changes.append({
                    "market": market["name"],
                    "market_type": market["market_type"],
                    "old_price": history[1]["price"],
                    "new_price": history[0]["price"],
                    "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                })
        changes.sort(key=lambda x: abs(x["change_pct"]), reverse=True)
        return changes[:10]

    async def get_investment_opportunities(self) -> list[dict]:
        markets = await market_engine.get_all_markets()
        opportunities = []
        for market in markets:
            if market["growth_rate"] > 0.05:
                opportunities.append({
                    "market": market["name"],
                    "market_type": market["market_type"],
                    "growth_rate": market["growth_rate"],
                    "current_price": market["current_price"],
                    "risk": "low" if market["growth_rate"] < 0.15 else "medium",
                    "recommendation": "Consider investing" if market["growth_rate"] > 0.1 else "Monitor",
                })
        opportunities.sort(key=lambda x: x["growth_rate"], reverse=True)
        return opportunities[:5]

    async def get_industry_report(self, industry: str) -> dict:
        markets = await market_engine.get_all_markets(industry)
        total_volume = sum(m["volume"] for m in markets)
        avg_growth = sum(m["growth_rate"] for m in markets) / len(markets) if markets else 0

        return {
            "industry": industry,
            "market_count": len(markets),
            "total_volume": total_volume,
            "average_growth_rate": round(avg_growth, 4),
            "markets": [
                {
                    "name": m["name"],
                    "price": m["current_price"],
                    "growth": m["growth_rate"],
                    "supply": m["supply"],
                    "demand": m["demand"],
                }
                for m in markets
            ],
        }

    async def get_economic_dashboard(self) -> dict:
        markets = await market_engine.get_all_markets()
        resources = resource_economy.get_resource_status()
        finance = await finance_engine.get_financial_overview()
        wealth = await wealth_distribution.analyze()

        recent_events = await eco_db.get_economic_events(limit=5)
        indicators = await eco_db.get_indicators(limit=10)

        return {
            "markets": {
                "total": len(markets),
                "active": len([m for m in markets if m["status"] == "active"]),
                "avg_price": round(
                    sum(m["current_price"] for m in markets) / len(markets), 2
                ) if markets else 0,
                "total_volume": sum(m["volume"] for m in markets),
            },
            "resources": resources,
            "finance": finance,
            "wealth": wealth,
            "recent_events": recent_events,
            "indicators": indicators,
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


economic_intelligence = EconomicIntelligence()
