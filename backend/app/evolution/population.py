import logging
import random

from app.simulation.identity import create_identity_data
from app.simulation.persistence import save_identity, save_personality, save_goal, save_skills, save_timeline_event
from app.resources.manager import resource_manager
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.evolution.population")

POPULATION_LIMITS = {
    "max_population": 500,
    "min_population": 20,
    "growth_rate_cap": 5,
    "compute_budget_per_agent": 100,
}


class PopulationEngine:
    def __init__(self):
        self.stats = {
            "citizens_generated": 0,
            "citizens_archived": 0,
            "growth_requests": 0,
            "growth_denied": 0,
        }

    async def evaluate_population_need(self, agent_count: int, company_count: int,
                                       task_count: int, open_tasks: int,
                                       economy_growth: float) -> dict:
        reasons = []
        should_grow = False

        if agent_count < POPULATION_LIMITS["min_population"]:
            reasons.append("Population below minimum threshold")
            should_grow = True

        if open_tasks > agent_count * 0.3 and agent_count < POPULATION_LIMITS["max_population"]:
            reasons.append(f"High task demand: {open_tasks} open tasks")
            should_grow = True

        if company_count > 0 and agent_count / max(company_count, 1) < 3:
            reasons.append("Low employee-to-company ratio")
            should_grow = True

        if economy_growth > 0.1:
            reasons.append("Strong economic growth")
            should_grow = True

        if agent_count >= POPULATION_LIMITS["max_population"]:
            reasons.append("Population at maximum capacity")
            should_grow = False

        self.stats["growth_requests"] += 1
        if not should_grow:
            self.stats["growth_denied"] += 1

        return {
            "should_grow": should_grow,
            "current_population": agent_count,
            "max_population": POPULATION_LIMITS["max_population"],
            "reasons": reasons,
            "suggested_growth": min(POPULATION_LIMITS["growth_rate_cap"],
                                    POPULATION_LIMITS["max_population"] - agent_count) if should_grow else 0,
        }

    async def generate_citizen(self, parent_agent_id: str | None = None,
                               parent_profile: dict | None = None,
                               lineage_id: str | None = None,
                               generation: int = 1,
                               specialization: str | None = None) -> dict:
        from app.simulation.engine import engine as sim_engine
        if len(sim_engine.agents) >= POPULATION_LIMITS["max_population"]:
            return {"success": False, "error": "Population at maximum"}

        from app.simulation.agents import SimAgent, create_agent
        agent_index = len(sim_engine.agents)
        agent = create_agent(agent_index)

        ident_data = create_identity_data(generation=generation)
        agent.name = ident_data["display_name"]

        if parent_profile and random.random() > 0.3:
            parent_personality = parent_profile.get("personality", {})
            for trait in ["curiosity", "creativity", "reliability", "risk_tolerance",
                          "patience", "leadership", "cooperation", "learning_speed"]:
                parent_val = parent_personality.get(trait, 50)
                mutation = random.gauss(0, 10)
                ident_data["personality"][trait] = max(0, min(100, parent_val + mutation))

        if parent_profile and random.random() > 0.4:
            parent_skills = parent_profile.get("skills", [])
            inherited_count = max(1, len(parent_skills) // 2)
            inherited = random.sample(parent_skills, min(inherited_count, len(parent_skills)))
            for ps in inherited:
                for ns in ident_data["skills"]:
                    if ns["skill_name"] == ps.get("skill_name"):
                        ns["level"] = max(1, ps.get("level", 1) - 1)
                        ns["experience"] = ps.get("experience", 0) // 2
                        break

        if specialization:
            spec_skills = {
                "research": ["Research Methods", "Data Analysis", "Scientific Writing"],
                "engineering": ["Software Development", "System Design", "DevOps"],
                "business": ["Strategy", "Finance", "Marketing"],
                "creative": ["Design", "Content Creation", "Brand Development"],
            }
            if specialization in spec_skills:
                for skill_name in spec_skills[specialization]:
                    if not any(s["skill_name"] == skill_name for s in ident_data["skills"]):
                        ident_data["skills"].append({
                            "skill_name": skill_name, "level": 1,
                            "experience": 0, "max_experience": 100,
                            "learning_progress": 0, "certified": False,
                        })

        sim_engine.agents.append(agent)
        from app.simulation.engine import AgentProfile
        sim_engine.profiles[agent.id] = AgentProfile(
            agent=agent,
            identity={
                "first_name": ident_data["first_name"],
                "last_name": ident_data["last_name"],
                "display_name": ident_data["display_name"],
                "generation": generation,
                "status": "active",
                "profession": ident_data["profession"],
                "profession_category": ident_data["profession_category"],
            },
            personality=ident_data["personality"],
            goal=ident_data["goal"],
            skills=ident_data["skills"],
            trust_score=ident_data.get("trust_score", 50),
        )

        await save_identity(agent.id, sim_engine.profiles[agent.id].identity)
        await save_personality(agent.id, sim_engine.profiles[agent.id].personality)
        await save_goal(agent.id, sim_engine.profiles[agent.id].goal)
        await save_skills(agent.id, sim_engine.profiles[agent.id].skills)
        await save_timeline_event(agent.id, 1, "Born", f"{agent.name} was born into generation {generation}")

        await resource_manager.init_agent(agent.id, initial_balance=50)

        self.stats["citizens_generated"] += 1

        await dispatch(Event(EventType.CITIZEN_GENERATED, {
            "agent_id": agent.id, "name": agent.name,
            "generation": generation, "parent_id": parent_agent_id,
            "lineage_id": lineage_id,
        }))

        return {
            "success": True,
            "agent_id": agent.id,
            "name": agent.name,
            "generation": generation,
            "profession": ident_data["profession"],
            "skills": len(ident_data["skills"]),
        }

    async def archive_citizen(self, agent_id: str) -> dict:
        from app.simulation.engine import engine as sim_engine
        agent = next((a for a in sim_engine.agents if a.id == agent_id), None)
        if not agent:
            return {"success": False, "error": "Agent not found"}

        agent.current_status = "archived"
        self.stats["citizens_archived"] += 1
        return {"success": True, "agent_id": agent_id, "status": "archived"}

    def get_state(self) -> dict:
        from app.simulation.engine import engine as sim_engine
        return {
            "stats": self.stats.copy(),
            "current_population": len(sim_engine.agents),
            "limits": POPULATION_LIMITS.copy(),
        }


population_engine = PopulationEngine()
