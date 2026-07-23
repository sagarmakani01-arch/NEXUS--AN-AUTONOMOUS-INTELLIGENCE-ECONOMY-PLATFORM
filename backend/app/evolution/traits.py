import logging
import random
import json

from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.evolution.traits")

TRAIT_DEFINITIONS = {
    "intelligence": {"name": "Intelligence", "category": "cognitive", "inheritable": True,
                     "mutation_rate": 0.15, "natural_selection_weight": 1.2},
    "creativity": {"name": "Creativity", "category": "cognitive", "inheritable": True,
                   "mutation_rate": 0.12, "natural_selection_weight": 1.0},
    "reliability": {"name": "Reliability", "category": "personality", "inheritable": True,
                    "mutation_rate": 0.08, "natural_selection_weight": 1.1},
    "risk_tolerance": {"name": "Risk Tolerance", "category": "personality", "inheritable": True,
                       "mutation_rate": 0.20, "natural_selection_weight": 0.8},
    "curiosity": {"name": "Curiosity", "category": "cognitive", "inheritable": True,
                  "mutation_rate": 0.18, "natural_selection_weight": 1.3},
    "patience": {"name": "Patience", "category": "personality", "inheritable": True,
                 "mutation_rate": 0.10, "natural_selection_weight": 0.9},
    "leadership": {"name": "Leadership", "category": "social", "inheritable": True,
                   "mutation_rate": 0.14, "natural_selection_weight": 1.0},
    "cooperation": {"name": "Cooperation", "category": "social", "inheritable": True,
                    "mutation_rate": 0.10, "natural_selection_weight": 1.1},
    "learning_speed": {"name": "Learning Speed", "category": "cognitive", "inheritable": True,
                       "mutation_rate": 0.12, "natural_selection_weight": 1.4},
    "emotional_intelligence": {"name": "Emotional Intelligence", "category": "social",
                               "inheritable": True, "mutation_rate": 0.10,
                               "natural_selection_weight": 1.0},
    "decisiveness": {"name": "Decisiveness", "category": "personality", "inheritable": True,
                     "mutation_rate": 0.12, "natural_selection_weight": 1.0},
    "resilience": {"name": "Resilience", "category": "personality", "inheritable": True,
                   "mutation_rate": 0.08, "natural_selection_weight": 1.2},
}

MUTATION_RANGES = {
    "small": 5,
    "medium": 10,
    "large": 15,
}


class TraitEvolutionEngine:
    def __init__(self):
        self.stats = {
            "mutations_occurred": 0,
            "selections_applied": 0,
            "traits_optimized": 0,
        }

    async def inherit_traits(self, parent_traits: dict, parent_reputation: float = 50) -> dict:
        child_traits = {}
        for trait_name, parent_val in parent_traits.items():
            defn = TRAIT_DEFINITIONS.get(trait_name, {})
            if not defn.get("inheritable", True):
                child_traits[trait_name] = parent_val
                continue

            mutation_rate = defn.get("mutation_rate", 0.1)
            if random.random() < mutation_rate:
                direction = 1 if random.random() > 0.5 else -1
                magnitude = random.choice(list(MUTATION_RANGES.values()))
                mutation = direction * random.uniform(1, magnitude)
                new_val = parent_val + mutation
                if parent_reputation > 60:
                    new_val += random.uniform(1, 3)
                new_val = max(0, min(100, new_val))
                child_traits[trait_name] = round(new_val, 2)
                self.stats["mutations_occurred"] += 1
            else:
                child_traits[trait_name] = round(parent_val + random.gauss(0, 2), 2)
                child_traits[trait_name] = max(0, min(100, child_traits[trait_name]))

        for trait_name, defn in TRAIT_DEFINITIONS.items():
            if trait_name not in child_traits:
                child_traits[trait_name] = round(random.uniform(30, 70), 2)

        return child_traits

    async def apply_selection_pressure(self, agent_traits: dict,
                                       fitness_score: float,
                                       population_avg: dict | None = None) -> dict:
        adjusted = agent_traits.copy()
        for trait_name, value in adjusted.items():
            defn = TRAIT_DEFINITIONS.get(trait_name, {})
            weight = defn.get("natural_selection_weight", 1.0)
            if population_avg and trait_name in population_avg:
                pop_avg = population_avg[trait_name]
                if fitness_score > 60:
                    if value > pop_avg:
                        adjusted[trait_name] = min(100, value + weight * 1)
                elif fitness_score < 40:
                    if value > pop_avg:
                        adjusted[trait_name] = max(0, value - weight * 0.5)
            self.stats["selections_applied"] += 1

        return adjusted

    async def calculate_fitness(self, agent_id: str) -> float:
        from app.simulation.engine import engine as sim_engine
        profile = sim_engine.profiles.get(agent_id)
        if not profile:
            return 0.0

        skills = profile.skills
        avg_skill = sum(s.get("level", 1) for s in skills) / max(len(skills), 1) if skills else 1
        skill_fitness = min(100, avg_skill * 10)

        reputation = profile.agent.reputation

        goal = profile.goal
        goal_progress = goal.get("progress", 0) if isinstance(goal, dict) else 0

        fitness = (
            skill_fitness * 0.3 +
            reputation * 0.3 +
            goal_progress * 0.2 +
            min(100, agent_id.__hash__() % 100) * 0.2
        )
        return round(min(100, max(0, fitness)), 2)

    async def optimize_traits(self, agent_id: str,
                              optimization_goal: str = "balanced") -> dict:
        from app.simulation.engine import engine as sim_engine
        profile = sim_engine.profiles.get(agent_id)
        if not profile:
            return {"optimized": False}

        personality = profile.personality
        if isinstance(personality, str):
            try:
                personality = json.loads(personality)
            except Exception:
                personality = {}

        optimized = personality.copy()

        if optimization_goal == "balanced":
            target = 50
            for trait in optimized:
                diff = target - optimized[trait]
                optimized[trait] = round(optimized[trait] + diff * 0.1, 2)
        elif optimization_goal == "performance":
            boost_traits = ["intelligence", "learning_speed", "decisiveness"]
            for t in boost_traits:
                if t in optimized:
                    optimized[t] = min(100, optimized[t] + random.uniform(1, 5))
        elif optimization_goal == "social":
            boost_traits = ["cooperation", "leadership", "emotional_intelligence"]
            for t in boost_traits:
                if t in optimized:
                    optimized[t] = min(100, optimized[t] + random.uniform(1, 5))

        self.stats["traits_optimized"] += 1
        return {
            "optimized": True,
            "old_traits": personality,
            "new_traits": optimized,
            "goal": optimization_goal,
        }

    def get_trait_definitions(self) -> dict:
        return TRAIT_DEFINITIONS.copy()

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "trait_definitions": TRAIT_DEFINITIONS,
        }


trait_evolution_engine = TraitEvolutionEngine()
