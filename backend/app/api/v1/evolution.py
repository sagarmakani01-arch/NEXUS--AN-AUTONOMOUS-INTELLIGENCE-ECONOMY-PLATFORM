from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.evolution.engine import evolution_engine
from app.evolution.population import population_engine
from app.evolution.lineage import lineage_system
from app.evolution.traits import trait_evolution_engine
from app.evolution.skills import skill_inheritance_engine
from app.evolution.mentorship import mentorship_engine
from app.evolution.civilization import civilization_engine
from app.evolution.innovation import innovation_system
from app.evolution import persistence as evo_db

router = APIRouter(prefix="/api/v1/evolution", tags=["evolution"])


# Engine control

@router.get("/engine/state")
async def get_engine_state():
    return evolution_engine.get_state()


@router.post("/engine/start")
async def start_engine():
    await evolution_engine.start()
    return {"status": "started"}


@router.post("/engine/stop")
async def stop_engine():
    await evolution_engine.stop()
    return {"status": "stopped"}


@router.post("/engine/tick")
async def manual_tick():
    await evolution_engine.tick()
    return {"status": "tick_completed", "generation": evolution_engine.generation}


@router.post("/engine/speed")
async def set_speed(interval: int = Query(ge=5, le=300)):
    evolution_engine.set_speed(interval)
    return {"tick_interval": interval}


# Population

@router.get("/population/state")
async def get_population_state():
    return population_engine.get_state()


@router.get("/population/evaluate")
async def evaluate_population(agent_count: int = 50, company_count: int = 5,
                              task_count: int = 10, open_tasks: int = 5,
                              economy_growth: float = 0.05):
    return await population_engine.evaluate_population_need(
        agent_count, company_count, task_count, open_tasks, economy_growth
    )


@router.post("/population/generate")
async def generate_citizen(parent_agent_id: str | None = None,
                           lineage_id: str | None = None,
                           generation: int = 1,
                           specialization: str | None = None):
    parent_profile = None
    if parent_agent_id:
        from app.simulation.engine import engine as sim_engine
        parent_profile = sim_engine.profiles.get(parent_agent_id)
        if parent_profile:
            parent_profile = {
                "personality": parent_profile.personality,
                "skills": parent_profile.skills,
            }
    return await population_engine.generate_citizen(
        parent_agent_id=parent_agent_id,
        parent_profile=parent_profile,
        lineage_id=lineage_id,
        generation=generation,
        specialization=specialization,
    )


@router.post("/population/archive/{agent_id}")
async def archive_citizen(agent_id: str):
    return await population_engine.archive_citizen(agent_id)


# Lineages

@router.get("/lineages")
async def list_lineages():
    return await lineage_system.list_lineages()


@router.get("/lineages/{lineage_id}")
async def get_lineage(lineage_id: str):
    result = await lineage_system.get_lineage(lineage_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lineage not found")
    return result


@router.post("/lineages")
async def create_lineage(founder_agent_id: str,
                         name: str | None = None,
                         parent_lineage_id: str | None = None):
    return await lineage_system.create_lineage(founder_agent_id, name, parent_lineage_id)


@router.get("/lineages/{lineage_id}/tree")
async def get_lineage_tree(lineage_id: str):
    return await lineage_system.get_lineage_tree(lineage_id)


@router.get("/lineages/{lineage_id}/performance")
async def get_lineage_performance(lineage_id: str):
    return await lineage_system.get_lineage_performance(lineage_id)


@router.post("/lineages/{lineage_id}/members")
async def add_lineage_member(lineage_id: str, agent_id: str):
    return await lineage_system.add_member(lineage_id, agent_id)


# Traits

@router.get("/traits/definitions")
async def get_trait_definitions():
    return trait_evolution_engine.get_trait_definitions()


@router.get("/traits/state")
async def get_traits_state():
    return trait_evolution_engine.get_state()


@router.post("/traits/inherit")
async def inherit_traits(parent_traits: dict, parent_reputation: float = 50):
    return await trait_evolution_engine.inherit_traits(parent_traits, parent_reputation)


@router.post("/traits/optimize/{agent_id}")
async def optimize_traits(agent_id: str, goal: str = "balanced"):
    return await trait_evolution_engine.optimize_traits(agent_id, goal)


# Skills

@router.get("/skills/tree")
async def get_skill_tree():
    return skill_inheritance_engine.get_skill_tree()


@router.get("/skills/synergies")
async def get_skill_synergies():
    return skill_inheritance_engine.get_synergies()


@router.get("/skills/state")
async def get_skills_state():
    return skill_inheritance_engine.get_state()


@router.post("/skills/generate-offspring")
async def generate_offspring_skills(parent_skills_a: list[dict],
                                    parent_skills_b: list[dict],
                                    parent_rep_a: float = 50,
                                    parent_rep_b: float = 50):
    return await skill_inheritance_engine.generate_offspring_skills(
        parent_skills_a, parent_skills_b, parent_rep_a, parent_rep_b
    )


# Mentorship

@router.get("/mentorship/state")
async def get_mentorship_state():
    return mentorship_engine.get_state()


@router.get("/mentorship/agent/{agent_id}")
async def get_agent_mentorships(agent_id: str):
    return await mentorship_engine.get_agent_mentorships(agent_id)


@router.get("/mentorship/find/{mentee_id}")
async def find_mentor(mentee_id: str, domain: str | None = None):
    result = await mentorship_engine.find_mentor(mentee_id, domain)
    if not result:
        raise HTTPException(status_code=404, detail="No mentor found")
    return result


@router.post("/mentorship/create")
async def create_mentorship(mentor_id: str, mentee_id: str):
    return await mentorship_engine.create_mentorship(mentor_id, mentee_id)


@router.post("/mentorship/session/{mentorship_id}")
async def conduct_session(mentorship_id: str):
    return await mentorship_engine.conduct_session(mentorship_id)


# Civilization

@router.get("/civilization/status")
async def get_civilization_status():
    return await civilization_engine.get_civilization_status()


@router.get("/civilization/state")
async def get_civilization_state():
    return civilization_engine.get_state()


@router.get("/civilization/suggestions")
async def get_adaptation_suggestions():
    return await civilization_engine.get_adaptation_suggestions()


@router.post("/civilization/event")
async def apply_civilization_event(event_type: str):
    return await civilization_engine.apply_event_impact(event_type)


# Innovation

@router.get("/innovation/state")
async def get_innovation_state():
    return innovation_system.get_state()


@router.get("/innovation/stats")
async def get_innovation_stats():
    return await innovation_system.get_innovation_stats()


@router.get("/innovation/types")
async def get_innovation_types():
    return innovation_system.get_innovation_types()


@router.get("/innovation/list")
async def list_innovations(discoverer_id: str | None = None,
                           innovation_type: str | None = None,
                           limit: int = Query(ge=1, le=100, default=20)):
    return await evo_db.list_innovations(discoverer_id, innovation_type, limit)


# Stats

@router.get("/stats")
async def get_evolution_stats():
    return await evo_db.get_evolution_stats()
