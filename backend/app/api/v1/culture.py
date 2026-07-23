from fastapi import APIRouter, HTTPException, Query

from app.culture.engine import culture_engine
from app.culture import persistence as db
from app.culture import identity as identity_engine
from app.culture import values as values_engine
from app.culture import traditions as traditions_engine
from app.culture import institutions as institutions_engine
from app.culture import communities as communities_engine
from app.culture import memory as memory_engine
from app.culture import dynamics as dynamics_engine
from app.culture import reputation as reputation_engine
from app.culture import evolution as evolution_engine

router = APIRouter(prefix="/api/v1/culture", tags=["culture"])


@router.get("/engine/state")
async def get_engine_state():
    return culture_engine.get_state()

@router.post("/engine/start")
async def start_engine():
    await culture_engine.start()
    return {"status": "started"}

@router.post("/engine/stop")
async def stop_engine():
    await culture_engine.stop()
    return {"status": "stopped"}


@router.get("/identity/{civ_id}")
async def get_identity(civ_id: str):
    result = await db.get_cultural_identity(civ_id)
    if not result:
        raise HTTPException(status_code=404, detail="Identity not found")
    return result

@router.post("/identity/{civ_id}/history")
async def add_history(civ_id: str, event: str, impact: float = 50.0):
    await identity_engine.add_to_history(civ_id, event, impact)
    return {"status": "added"}

@router.post("/identity/{civ_id}/symbol")
async def add_symbol(civ_id: str, symbol: str):
    await identity_engine.add_symbol(civ_id, symbol)
    return {"status": "added"}

@router.post("/identity/{civ_id}/goal")
async def add_goal(civ_id: str, goal: str):
    await identity_engine.add_goal(civ_id, goal)
    return {"status": "added"}

@router.post("/identity/{civ_id}/norm")
async def add_norm(civ_id: str, norm: str):
    await identity_engine.add_norm(civ_id, norm)
    return {"status": "added"}


@router.get("/values/{civ_id}")
async def get_values(civ_id: str):
    result = await db.get_value_system(civ_id)
    if not result:
        raise HTTPException(status_code=404, detail="Values not found")
    return result

@router.post("/values/{civ_id}/shift")
async def shift_value(civ_id: str, value_name: str, delta: float):
    result = await values_engine.shift_value(civ_id, value_name, delta)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid value or civ")
    return result

@router.post("/values/{civ_id}/event")
async def apply_event(civ_id: str, event_type: str):
    result = await values_engine.apply_event_influence(civ_id, event_type)
    return result or {"status": "no_change"}


@router.get("/traditions")
async def list_traditions(civ_id: str | None = None):
    return await db.list_traditions(civ_id)

@router.post("/traditions/create")
async def create_tradition(civ_id: str, name: str,
                           description: str | None = None,
                           frequency: str = "annual",
                           impact: float = 20.0):
    return await traditions_engine.create_tradition(civ_id, name, description, frequency, impact)

@router.post("/traditions/{trad_id}/hold")
async def hold_tradition(trad_id: str):
    result = await traditions_engine.hold_tradition(trad_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tradition not found")
    return result


@router.get("/institutions")
async def list_institutions(civ_id: str | None = None, inst_type: str | None = None):
    return await db.list_institutions(civ_id, inst_type=inst_type)

@router.get("/institutions/{inst_id}")
async def get_institution(inst_id: str):
    result = await db.get_institution(inst_id)
    if not result:
        raise HTTPException(status_code=404, detail="Institution not found")
    return result

@router.post("/institutions/create")
async def create_institution(civ_id: str, name: str,
                             inst_type: str | None = None,
                             description: str | None = None):
    return await institutions_engine.create_institution(civ_id, name, inst_type, description)

@router.post("/institutions/{inst_id}/strengthen")
async def strengthen_institution(inst_id: str, amount: float = 5.0):
    result = await institutions_engine.strengthen_institution(inst_id, amount)
    if not result:
        raise HTTPException(status_code=404, detail="Institution not found")
    return result


@router.get("/communities")
async def list_communities(civ_id: str | None = None):
    return await db.list_communities(civ_id)

@router.get("/communities/{comm_id}")
async def get_community(comm_id: str):
    result = await db.get_community(comm_id)
    if not result:
        raise HTTPException(status_code=404, detail="Community not found")
    return result

@router.post("/communities/create")
async def create_community(civ_id: str, name: str,
                           community_type: str | None = None,
                           description: str | None = None):
    return await communities_engine.create_community(civ_id, name, community_type, description)

@router.post("/communities/{comm_id}/join")
async def join_community(comm_id: str, entity_id: str,
                         entity_type: str = "agent", role: str = "member"):
    result = await communities_engine.join_community(comm_id, entity_id, entity_type, role)
    if not result:
        raise HTTPException(status_code=404, detail="Community not found")
    return result

@router.post("/communities/{comm_id}/leave")
async def leave_community(comm_id: str, entity_id: str):
    result = await communities_engine.leave_community(comm_id, entity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Community not found")
    return result

@router.get("/communities/{comm_id}/members")
async def list_members(comm_id: str):
    return await db.list_community_members(comm_id)


@router.get("/memory/{civ_id}")
async def get_memories(civ_id: str, event_type: str | None = None,
                       limit: int = Query(ge=1, le=200, default=50)):
    return await memory_engine.get_memories(civ_id, event_type=event_type, limit=limit)

@router.post("/memory/record")
async def record_memory(civ_id: str, event_type: str, title: str,
                        description: str | None = None, impact: float = 50.0):
    return await memory_engine.record_major_event(civ_id, event_type, title, description, impact)


@router.get("/dynamics/{civ_id}")
async def get_dynamics(civ_id: str):
    result = await db.get_social_dynamics(civ_id)
    if not result:
        raise HTTPException(status_code=404, detail="Dynamics not found")
    return result

@router.post("/dynamics/{civ_id}/interact")
async def record_interaction(civ_id: str, interaction_type: str):
    result = await dynamics_engine.record_interaction(civ_id, interaction_type)
    return result or {"status": "no_change"}


@router.get("/reputation/{civ_id}")
async def get_reputation(civ_id: str, entity_type: str | None = None,
                         limit: int = Query(ge=1, le=100, default=20)):
    return await reputation_engine.get_rankings(civ_id, entity_type=entity_type, limit=limit)

@router.post("/reputation/contribute")
async def record_contribution(civ_id: str, entity_id: str,
                              entity_type: str = "agent",
                              influence_delta: float = 5.0):
    return await reputation_engine.record_contribution(civ_id, entity_id, entity_type, influence_delta)


@router.get("/evolution/{civ_id}")
async def get_identity_score(civ_id: str):
    result = await db.get_identity_score(civ_id)
    if not result:
        result = await evolution_engine.calculate_identity_score(civ_id)
    return result

@router.post("/evolution/{civ_id}/evolve")
async def trigger_evolution(civ_id: str):
    await evolution_engine.evolve_values(civ_id)
    await evolution_engine.evolve_institutions(civ_id)
    result = await evolution_engine.evolve_social_norms(civ_id)
    score = await evolution_engine.calculate_identity_score(civ_id)
    return {"norm_change": result, "identity_score": score}


@router.get("/stats")
async def get_stats():
    return await db.get_culture_stats()

@router.get("/timeline/{civ_id}")
async def get_timeline(civ_id: str, limit: int = Query(ge=1, le=200, default=50)):
    return await db.list_cultural_timeline(civ_id, limit=limit)
