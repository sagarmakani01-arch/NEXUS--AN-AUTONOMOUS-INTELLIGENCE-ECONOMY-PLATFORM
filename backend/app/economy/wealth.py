import logging
import statistics

from app.resources.persistence import get_all_wallets

logger = logging.getLogger("nexus.economy.wealth")


class WealthDistribution:
    def __init__(self):
        self.history: list[dict] = []
        self.stats = {
            "total_wealth": 0.0,
            "average_wealth": 0.0,
            "median_wealth": 0.0,
            "gini_coefficient": 0.0,
            "top_10_pct_ownership": 0.0,
            "wealthiest_agent": None,
            "poorest_agent": None,
        }

    async def analyze(self) -> dict:
        wallets = await get_all_wallets()
        if not wallets:
            return self.stats

        balances = [w.get("balance", 0) for w in wallets]
        total = sum(balances)

        self.stats["total_wealth"] = round(total, 2)
        self.stats["average_wealth"] = round(total / len(balances), 2) if balances else 0
        self.stats["median_wealth"] = round(statistics.median(balances), 2) if balances else 0

        sorted_balances = sorted(balances, reverse=True)
        top_10_count = max(1, len(sorted_balances) // 10)
        top_10_wealth = sum(sorted_balances[:top_10_count])
        self.stats["top_10_pct_ownership"] = round(
            top_10_wealth / total * 100, 2
        ) if total > 0 else 0

        self.stats["gini_coefficient"] = self._calculate_gini(balances)

        if wallets:
            wealthiest = max(wallets, key=lambda w: w.get("balance", 0))
            poorest = min(wallets, key=lambda w: w.get("balance", 0))
            self.stats["wealthiest_agent"] = {
                "agent_id": wealthiest.get("agent_id"),
                "balance": wealthiest.get("balance", 0),
            }
            self.stats["poorest_agent"] = {
                "agent_id": poorest.get("agent_id"),
                "balance": poorest.get("balance", 0),
            }

        self.history.append({
            "total_wealth": self.stats["total_wealth"],
            "average_wealth": self.stats["average_wealth"],
            "median_wealth": self.stats["median_wealth"],
            "gini_coefficient": self.stats["gini_coefficient"],
            "top_10_pct_ownership": self.stats["top_10_pct_ownership"],
        })
        if len(self.history) > 100:
            self.history = self.history[-100:]

        return self.stats

    def _calculate_gini(self, values: list[float]) -> float:
        if not values or len(values) < 2:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        total = sum(sorted_vals)
        if total == 0:
            return 0.0
        cumulative = 0.0
        gini_sum = 0.0
        for i, val in enumerate(sorted_vals):
            cumulative += val
            gini_sum += (2 * (i + 1) - n - 1) * val
        return round(gini_sum / (n * total), 4)

    def get_wealth_trend(self) -> list[dict]:
        return self.history[-20:]

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "history_length": len(self.history),
        }


wealth_distribution = WealthDistribution()
