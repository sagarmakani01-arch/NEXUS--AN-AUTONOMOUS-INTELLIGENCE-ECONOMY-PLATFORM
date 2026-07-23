import logging
import random

from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.economy.resources")

RESOURCE_TYPES = {
    "compute_credits": {
        "name": "Compute Credits",
        "base_production": 5,
        "base_consumption": 2,
        "scarcity_threshold": 50,
        "description": "Energy for agent decision-making",
    },
    "memory_capacity": {
        "name": "Memory Capacity",
        "base_production": 10,
        "base_consumption": 3,
        "scarcity_threshold": 100,
        "description": "Storage for agent memories and data",
    },
    "storage": {
        "name": "Storage",
        "base_production": 20,
        "base_consumption": 5,
        "scarcity_threshold": 200,
        "description": "Persistent data storage",
    },
    "knowledge": {
        "name": "Knowledge",
        "base_production": 2,
        "base_consumption": 1,
        "scarcity_threshold": 30,
        "description": "Accumulated expertise and information",
    },
    "capital": {
        "name": "Capital",
        "base_production": 50,
        "base_consumption": 20,
        "scarcity_threshold": 500,
        "description": "Financial resources for investment",
    },
}


class ResourceEconomy:
    def __init__(self):
        self.global_supply = {rtype: 0 for rtype in RESOURCE_TYPES}
        self.global_demand = {rtype: 0 for rtype in RESOURCE_TYPES}
        self.scarcity_levels = {rtype: "normal" for rtype in RESOURCE_TYPES}
        self.prices = {rtype: config["base_production"] for rtype, config in RESOURCE_TYPES.items()}
        self.stats = {
            "shortages": 0,
            "surpluses": 0,
            "price_adjustments": 0,
        }

    async def initialize(self, agent_count: int) -> None:
        for rtype, config in RESOURCE_TYPES.items():
            self.global_supply[rtype] = agent_count * config["base_production"]
            self.global_demand[rtype] = agent_count * config["base_consumption"]
            self._update_scarcity(rtype)

    def _update_scarcity(self, rtype: str) -> None:
        supply = self.global_supply[rtype]
        demand = self.global_demand[rtype]
        config = RESOURCE_TYPES[rtype]

        if demand == 0:
            self.scarcity_levels[rtype] = "surplus"
            return

        ratio = supply / max(demand, 1)
        if ratio < 0.5:
            self.scarcity_levels[rtype] = "critical"
        elif ratio < 0.8:
            self.scarcity_levels[rtype] = "scarce"
        elif ratio < 1.2:
            self.scarcity_levels[rtype] = "normal"
        elif ratio < 2.0:
            self.scarcity_levels[rtype] = "abundant"
        else:
            self.scarcity_levels[rtype] = "surplus"

    def update_prices(self) -> None:
        for rtype in RESOURCE_TYPES:
            supply = self.global_supply[rtype]
            demand = self.global_demand[rtype]
            current_price = self.prices[rtype]
            base = RESOURCE_TYPES[rtype]["base_production"]

            if demand > supply:
                scarcity = min(3.0, demand / max(supply, 1))
                price_change = scarcity * 0.05 * current_price
            elif supply > demand * 1.5:
                surplus = min(2.0, supply / max(demand, 1))
                price_change = -surplus * 0.03 * current_price
            else:
                price_change = 0.0

            noise = random.gauss(0, current_price * 0.01)
            new_price = current_price + price_change + noise
            new_price = max(base * 0.2, min(base * 5.0, new_price))

            if abs(new_price - current_price) > 0.01:
                self.prices[rtype] = round(new_price, 2)
                self.stats["price_adjustments"] += 1
                self._update_scarcity(rtype)

    def produce(self, rtype: str, amount: int, producer_type: str = "agent") -> int:
        if rtype not in RESOURCE_TYPES:
            return 0
        actual = min(amount, RESOURCE_TYPES[rtype]["base_production"] * 3)
        self.global_supply[rtype] += actual
        self._update_scarcity(rtype)
        return actual

    def consume(self, rtype: str, amount: int, consumer_type: str = "agent") -> bool:
        if rtype not in RESOURCE_TYPES:
            return False
        if self.global_supply[rtype] < amount:
            return False
        self.global_supply[rtype] -= amount
        self.global_demand[rtype] += amount // 2
        self._update_scarcity(rtype)
        if self.scarcity_levels[rtype] in ("critical", "scarce"):
            self.stats["shortages"] += 1
            return False
        return True

    def get_resource_status(self) -> dict:
        status = {}
        for rtype, config in RESOURCE_TYPES.items():
            supply = self.global_supply[rtype]
            demand = self.global_demand[rtype]
            status[rtype] = {
                "name": config["name"],
                "description": config["description"],
                "supply": supply,
                "demand": demand,
                "price": self.prices[rtype],
                "scarcity": self.scarcity_levels[rtype],
                "ratio": round(supply / max(demand, 1), 2),
            }
        return status

    def get_state(self) -> dict:
        return {
            "resources": self.get_resource_status(),
            "stats": self.stats.copy(),
        }


resource_economy = ResourceEconomy()
