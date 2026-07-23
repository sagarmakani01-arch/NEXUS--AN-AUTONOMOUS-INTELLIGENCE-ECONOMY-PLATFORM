import logging
import random

from app.economy import persistence as eco_db

logger = logging.getLogger("nexus.economy.pricing")


class PricingEngine:
    def __init__(self):
        self.factors = {
            "demand_weight": 0.30,
            "supply_weight": 0.25,
            "quality_weight": 0.15,
            "reputation_weight": 0.10,
            "competition_weight": 0.10,
            "trend_weight": 0.10,
        }
        self.stats = {"calculations": 0}

    def calculate_dynamic_price(self, base_price: float, supply: int, demand: int,
                                quality: float = 0.5, reputation: float = 0.5,
                                competition_count: int = 1, historical_trend: float = 0.0) -> float:
        demand_factor = demand / max(supply, 1)
        demand_component = min(3.0, demand_factor) * self.factors["demand_weight"]

        supply_scarcity = max(0.1, 1.0 - min(1.0, supply / max(demand + supply, 1)))
        supply_component = supply_scarcity * self.factors["supply_weight"]

        quality_component = quality * self.factors["quality_weight"]

        reputation_component = reputation * self.factors["reputation_weight"]

        competition_pressure = max(0.5, 1.0 - (competition_count - 1) * 0.05)
        competition_component = competition_pressure * self.factors["competition_weight"]

        trend_component = historical_trend * self.factors["trend_weight"]

        multiplier = (1.0 + demand_component + supply_component + quality_component +
                      reputation_component + competition_component + trend_component)

        noise = random.gauss(0, 0.02)
        multiplier += noise

        multiplier = max(0.1, min(5.0, multiplier))
        final_price = base_price * multiplier

        self.stats["calculations"] += 1
        return round(final_price, 2)

    def calculate_task_reward(self, skills: list[str], difficulty: str = "medium",
                              market_demand: float = 1.0) -> float:
        base_rewards = {"easy": 20, "medium": 50, "hard": 100, "expert": 200}
        base = base_rewards.get(difficulty, 50)

        skill_multiplier = 1.0 + len(skills) * 0.1
        demand_multiplier = max(0.5, min(2.0, market_demand))

        final = base * skill_multiplier * demand_multiplier
        noise = random.gauss(0, final * 0.05)
        final += noise

        return round(max(5.0, min(500.0, final)), 2)

    def calculate_salary(self, role: str, skill_level: int, industry: str,
                         market_supply: int = 100, market_demand: int = 100) -> float:
        base_salaries = {
            "employee": 50, "senior": 80, "lead": 100,
            "manager": 120, "director": 160, "vp": 200, "c_level": 300,
        }
        base = base_salaries.get(role, 50)

        skill_bonus = skill_level * 10

        if market_demand > market_supply:
            demand_premium = min(2.0, market_demand / max(market_supply, 1))
        else:
            demand_premium = max(0.7, market_supply / max(market_demand, 1))

        final = (base + skill_bonus) * demand_premium
        noise = random.gauss(0, final * 0.05)
        final += noise

        return round(max(20.0, min(500.0, final)), 2)

    def calculate_investment_return(self, amount: float, risk_level: str,
                                    market_conditions: float = 1.0) -> dict:
        risk_returns = {
            "very_low": {"min": 0.02, "max": 0.05, "failure_chance": 0.02},
            "low": {"min": 0.05, "max": 0.10, "failure_chance": 0.05},
            "medium": {"min": 0.08, "max": 0.18, "failure_chance": 0.10},
            "high": {"min": 0.15, "max": 0.35, "failure_chance": 0.20},
            "very_high": {"min": 0.25, "max": 0.60, "failure_chance": 0.35},
        }
        config = risk_returns.get(risk_level, risk_returns["medium"])

        if random.random() < config["failure_chance"]:
            loss_pct = random.uniform(0.3, 1.0)
            return {
                "success": False,
                "return_pct": -loss_pct,
                "return_amount": -amount * loss_pct,
                "risk_level": risk_level,
            }

        base_return = random.uniform(config["min"], config["max"])
        adjusted_return = base_return * market_conditions
        return_amount = amount * adjusted_return

        return {
            "success": True,
            "return_pct": round(adjusted_return, 4),
            "return_amount": round(return_amount, 2),
            "risk_level": risk_level,
        }

    def calculate_interest_rate(self, credit_score: float, loan_term_days: int,
                                economic_conditions: float = 1.0) -> float:
        base_rate = 0.05

        if credit_score >= 80:
            credit_factor = 0.6
        elif credit_score >= 60:
            credit_factor = 0.8
        elif credit_score >= 40:
            credit_factor = 1.0
        elif credit_score >= 20:
            credit_factor = 1.3
        else:
            credit_factor = 1.8

        term_factor = 1.0 + (loan_term_days / 365) * 0.02

        economic_factor = economic_conditions

        rate = base_rate * credit_factor * term_factor * economic_factor
        return round(max(0.01, min(0.30, rate)), 4)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy(), "factors": self.factors.copy()}


pricing_engine = PricingEngine()
