import logging
import random

from app.federation import persistence as db

logger = logging.getLogger("nexus.federation.competition")

COMPETITION_TYPES = ["technology_race", "economic", "innovation", "market_influence"]


class CompetitionEngine:
    def __init__(self):
        self.stats = {"competitions": 0, "milestones": 0}

    async def run_competition(self, civ_a_id: str, civ_b_id: str,
                              competition_type: str | None = None) -> dict:
        comp_type = competition_type or random.choice(COMPETITION_TYPES)
        civ_a = await db.get_civilization(civ_a_id)
        civ_b = await db.get_civilization(civ_b_id)
        if not civ_a or not civ_b:
            return {"success": False, "error": "Civilization not found"}

        score_a = self._calculate_score(civ_a, comp_type)
        score_b = self._calculate_score(civ_b, comp_type)
        winner = civ_a_id if score_a > score_b else civ_b_id

        self.stats["competitions"] += 1
        await db.record_history(winner, "competition_won",
                                f"Won {comp_type} competition",
                                impact_score=abs(score_a - score_b),
                                related_civilization_id=civ_b_id if winner == civ_a_id else civ_a_id)
        return {
            "competition_type": comp_type,
            "civilization_a_score": round(score_a, 2),
            "civilization_b_score": round(score_b, 2),
            "winner": winner,
        }

    def _calculate_score(self, civ: dict, comp_type: str) -> float:
        weights = {
            "technology_race": {"technology_level": 0.5, "research_output": 0.3, "economic_power": 0.2},
            "economic": {"economic_power": 0.5, "population": 0.2, "happiness": 0.3},
            "innovation": {"research_output": 0.4, "technology_level": 0.3, "cultural_influence": 0.3},
            "market_influence": {"economic_power": 0.4, "cultural_influence": 0.3, "reputation": 0.3},
        }
        w = weights.get(comp_type, weights["technology_race"])
        score = 0
        for key, weight in w.items():
            val = civ.get(key, 0)
            if key == "population":
                val = min(val / 100, 10)
            elif key in ("economic_power", "happiness", "cultural_influence", "reputation"):
                val = val / 10
            elif key == "technology_level":
                val = val * 5
            score += val * weight
        return score

    async def get_rankings(self) -> dict:
        civs = await db.list_civilizations()
        tech_ranked = sorted(civs, key=lambda c: c.get("technology_level", 0), reverse=True)
        econ_ranked = sorted(civs, key=lambda c: c.get("economic_power", 0), reverse=True)
        innov_ranked = sorted(civs, key=lambda c: c.get("research_output", 0), reverse=True)
        return {
            "technology": [{"name": c["name"], "score": c["technology_level"]} for c in tech_ranked[:10]],
            "economic": [{"name": c["name"], "score": c["economic_power"]} for c in econ_ranked[:10]],
            "innovation": [{"name": c["name"], "score": c["research_output"]} for c in innov_ranked[:10]],
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


competition_engine = CompetitionEngine()
