import logging
import random
import json

from app.evolution import persistence as evo_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.evolution.civilization")

CIVILIZATION_AXES = {
    "technology": {"name": "Technology Level", "base": 20, "growth_rate": 0.02,
                   "decay_rate": 0.01, "max_value": 1000},
    "culture": {"name": "Cultural Sophistication", "base": 10, "growth_rate": 0.015,
                "decay_rate": 0.008, "max_value": 500},
    "governance": {"name": "Governance Efficiency", "base": 15, "growth_rate": 0.01,
                   "decay_rate": 0.005, "max_value": 400},
    "economy": {"name": "Economic Output", "base": 25, "growth_rate": 0.025,
                "decay_rate": 0.012, "max_value": 800},
    "research": {"name": "Research Capacity", "base": 10, "growth_rate": 0.018,
                 "decay_rate": 0.009, "max_value": 600},
    "social": {"name": "Social Cohesion", "base": 15, "growth_rate": 0.012,
               "decay_rate": 0.006, "max_value": 400},
    "military": {"name": "Military Strength", "base": 5, "growth_rate": 0.008,
                 "decay_rate": 0.004, "max_value": 300},
    "environmental": {"name": "Environmental Health", "base": 50, "growth_rate": 0.005,
                      "decay_rate": 0.015, "max_value": 200},
}

EVENTS_IMPACT = {
    "boom": {"technology": 15, "economy": 20, "culture": 5},
    "recession": {"technology": -10, "economy": -15, "social": -5},
    "innovation": {"technology": 25, "research": 20, "economy": 10},
    "conflict": {"military": 15, "social": -10, "economy": -5, "environmental": -5},
    "discovery": {"research": 30, "technology": 10, "culture": 5},
    "cultural_shift": {"culture": 20, "social": 10, "governance": 5},
    "natural_disaster": {"environmental": -15, "economy": -10, "social": -10},
    "trade_agreement": {"economy": 15, "social": 5, "governance": 5},
}


class CivilizationAdaptationEngine:
    def __init__(self):
        self.current_level = 1
        self.generation_count = 0
        self.civilization_stats = {
            "total_innovations": 0,
            "total_events": 0,
            "level_changes": 0,
            "adaptations_applied": 0,
        }
        self._metrics_cache: dict[str, float] = {}
        for axis, defn in CIVILIZATION_AXES.items():
            self._metrics_cache[axis] = float(defn["base"])

    async def update_civilization(self, agent_count: int, company_count: int,
                                  total_innovations: int,
                                  economy_growth: float = 0.0) -> dict:
        changes = {}
        for axis, defn in CIVILIZATION_AXES.items():
            current = self._metrics_cache.get(axis, defn["base"])
            base = defn["base"]
            growth = defn["growth_rate"]
            decay = defn["decay_rate"]

            agent_factor = min(agent_count / 100, 2.0) * growth * base
            innovation_factor = min(total_innovations / 50, 2.0) * growth * base * 0.5
            economy_factor = economy_growth * growth * base * 0.3
            decay_factor = current * decay

            change = agent_factor + innovation_factor + economy_factor - decay_factor
            change += random.uniform(-2, 2)

            new_value = max(0, min(defn["max_value"], current + change))
            self._metrics_cache[axis] = round(new_value, 2)
            changes[axis] = round(new_value - current, 2)

        self.generation_count += 1
        self._check_level_up()

        for axis, value in self._metrics_cache.items():
            defn = CIVILIZATION_AXES[axis]
            old = value - changes.get(axis, 0)
            await evo_db.record_metric(
                f"civilization.{axis}", value,
                previous_value=old,
                metadata={"generation": self.generation_count},
            )

        await dispatch(Event(EventType.CIVILIZATION_EVOLVED, {
            "level": self.current_level,
            "generation": self.generation_count,
            "changes": changes,
            "axes": dict(self._metrics_cache),
        }))

        return {
            "level": self.current_level,
            "generation": self.generation_count,
            "changes": changes,
            "axes": dict(self._metrics_cache),
        }

    def _check_level_up(self):
        total = sum(self._metrics_cache.values())
        avg = total / len(self._metrics_cache) if self._metrics_cache else 0
        new_level = max(1, int(avg / 50))
        if new_level > self.current_level:
            self.current_level = new_level
            self.civilization_stats["level_changes"] += 1

    async def apply_event_impact(self, event_type: str) -> dict:
        impacts = EVENTS_IMPACT.get(event_type, {})
        applied = {}
        for axis, delta in impacts.items():
            if axis in self._metrics_cache:
                defn = CIVILIZATION_AXES[axis]
                self._metrics_cache[axis] = max(0, min(
                    defn["max_value"],
                    self._metrics_cache[axis] + delta,
                ))
                applied[axis] = delta
        self.civilization_stats["total_events"] += 1
        self.civilization_stats["adaptations_applied"] += len(applied)
        return {"event_type": event_type, "impacts": applied}

    async def get_civilization_status(self) -> dict:
        total = sum(self._metrics_cache.values())
        avg = total / len(self._metrics_cache) if self._metrics_cache else 0
        return {
            "level": self.current_level,
            "generation": self.generation_count,
            "total_score": round(total, 2),
            "average_score": round(avg, 2),
            "axes": dict(self._metrics_cache),
            "axis_definitions": {k: v["name"] for k, v in CIVILIZATION_AXES.items()},
            "stats": self.civilization_stats.copy(),
        }

    async def get_adaptation_suggestions(self) -> list[dict]:
        suggestions = []
        for axis, value in self._metrics_cache.items():
            defn = CIVILIZATION_AXES[axis]
            if value < defn["base"] * 0.5:
                suggestions.append({
                    "axis": axis,
                    "current": value,
                    "target": defn["base"],
                    "priority": "high",
                    "suggestion": f"Improve {defn['name']} through focused development",
                })
            elif value < defn["base"]:
                suggestions.append({
                    "axis": axis,
                    "current": value,
                    "target": defn["base"],
                    "priority": "medium",
                    "suggestion": f"Monitor {defn['name']} for potential decline",
                })
        return suggestions

    def get_state(self) -> dict:
        return {
            "level": self.current_level,
            "generation": self.generation_count,
            "metrics": dict(self._metrics_cache),
            "stats": self.civilization_stats.copy(),
        }


civilization_engine = CivilizationAdaptationEngine()
