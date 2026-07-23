import logging
import random

from app.evolution import persistence as evo_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.evolution.innovation")

INNOVATION_TYPES = {
    "technological": {"base_potential": 0.6, "impact_multiplier": 1.2,
                      "knowledge_domains": ["Software Development", "Machine Learning",
                                            "System Design", "Data Engineering"]},
    "scientific": {"base_potential": 0.7, "impact_multiplier": 1.5,
                   "knowledge_domains": ["Research Methods", "Data Analysis",
                                         "Scientific Writing", "Statistics"]},
    "economic": {"base_potential": 0.5, "impact_multiplier": 1.0,
                 "knowledge_domains": ["Finance", "Strategy", "Market Research", "Marketing"]},
    "social": {"base_potential": 0.4, "impact_multiplier": 0.8,
               "knowledge_domains": ["Leadership", "Communication", "Negotiation",
                                     "Public Speaking"]},
    "artistic": {"base_potential": 0.5, "impact_multiplier": 0.9,
                 "knowledge_domains": ["Design", "Content Creation", "Brand Development",
                                       "Graphic Design"]},
}

INNOVATION_TITLES = {
    "technological": ["{skill} Framework", "Advanced {skill} Protocol", "Next-Gen {skill} System",
                      "{skill} Optimization Engine", "Smart {skill} Platform"],
    "scientific": ["{skill} Theory", "New {skill} Methodology", "{skill} Research Breakthrough",
                   "Advanced {skill} Analysis", "{skill} Discovery"],
    "economic": ["{skill} Strategy", "Market {skill} Model", "{skill} Growth Framework",
                 "Digital {skill} Platform", "{skill} Optimization"],
    "social": ["{skill} Communication Model", "Community {skill} Framework",
               "{skill} Leadership System", "Social {skill} Protocol", "{skill} Network"],
    "artistic": ["{skill} Design System", "{skill} Creative Framework",
                 "Digital {skill} Platform", "{skill} Expression Engine", "{skill} Studio"],
}


class InnovationSystem:
    def __init__(self):
        self.stats = {
            "innovations_discovered": 0,
            "innovations_performed": 0,
            "breakthroughs": 0,
        }

    async def attempt_innovation(self, agent_id: str) -> dict | None:
        from app.simulation.engine import engine as sim_engine
        profile = sim_engine.profiles.get(agent_id)
        if not profile:
            return None

        skills = profile.skills
        if not skills:
            return None

        total_skill_level = sum(s.get("level", 1) for s in skills)
        max_level = max((s.get("level", 1) for s in skills), default=1)
        reputation = profile.agent.reputation

        innovation_score = (total_skill_level / max(len(skills), 1)) * 0.3 + \
                          max_level * 0.3 + reputation * 0.2 + random.uniform(0, 20)

        if innovation_score < 15:
            return None

        innovation_type = random.choice(list(INNOVATION_TYPES.keys()))
        type_config = INNOVATION_TYPES[innovation_type]
        domain = random.choice(type_config["knowledge_domains"])

        title_pattern = random.choice(INNOVATION_TITLES[innovation_type])
        best_skill = max(skills, key=lambda s: s.get("level", 1))["skill_name"]
        title = title_pattern.format(skill=best_skill)

        impact_score = min(100, innovation_score * type_config["impact_multiplier"])
        potential = type_config["base_potential"] * (1 + max_level / 20)

        innovation_id = await evo_db.create_innovation(
            discoverer_id=agent_id,
            innovation_type=innovation_type,
            title=title,
            description=f"A {innovation_type} innovation discovered by {profile.agent.name} "
                        f"leveraging expertise in {domain}",
            knowledge_domain=domain,
            impact_score=round(impact_score, 2),
            innovation_potential=round(potential, 3),
        )
        self.stats["innovations_discovered"] += 1

        if impact_score > 80:
            self.stats["breakthroughs"] += 1

        await dispatch(Event(EventType.INNOVATION_DISCOVERED, {
            "innovation_id": innovation_id,
            "agent_id": agent_id,
            "type": innovation_type,
            "title": title,
            "impact": impact_score,
            "domain": domain,
        }))

        return {
            "innovation_id": innovation_id,
            "type": innovation_type,
            "title": title,
            "domain": domain,
            "impact_score": round(impact_score, 2),
            "potential": round(potential, 3),
            "is_breakthrough": impact_score > 80,
        }

    async def get_innovation_stats(self) -> dict:
        all_innovations = await evo_db.list_innovations(limit=100)
        type_counts = {}
        for inn in all_innovations:
            t = inn.get("innovation_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

        avg_impact = 0
        if all_innovations:
            avg_impact = sum(i.get("impact_score", 0) for i in all_innovations) / len(all_innovations)

        return {
            "stats": self.stats.copy(),
            "type_distribution": type_counts,
            "total_innovations": len(all_innovations),
            "average_impact": round(avg_impact, 2),
            "breakthrough_rate": round(
                self.stats["breakthroughs"] / max(self.stats["innovations_discovered"], 1), 3
            ),
        }

    def get_innovation_types(self) -> dict:
        return INNOVATION_TYPES.copy()

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "types": list(INNOVATION_TYPES.keys()),
        }


innovation_system = InnovationSystem()
