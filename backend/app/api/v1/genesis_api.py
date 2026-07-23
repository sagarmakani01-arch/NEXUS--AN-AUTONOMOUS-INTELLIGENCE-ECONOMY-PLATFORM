from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.genesis.engine import genesis_engine
from app.genesis.persistence import genesis_db
from app.genesis.science import science_engine
from app.genesis.awareness import awareness_engine
from app.genesis.mythology import mythology_engine
from app.genesis.interaction import interaction_engine

router = APIRouter(prefix="/api/v1/genesis", tags=["Genesis"])


class CreateCivRequest(BaseModel):
    name: str


class CreatorEventRequest(BaseModel):
    interaction_type: Optional[str] = None
    custom_description: Optional[str] = None
    custom_interpretation: Optional[str] = None


# --- State ---

@router.get("/state")
async def get_genesis_state():
    return await genesis_engine.get_full_state()


# --- Civilizations ---

@router.post("/civilizations")
async def create_civilization(request: CreateCivRequest):
    return await genesis_engine.create_civilization(request.name)


@router.get("/civilizations")
async def list_civilizations():
    return {"civilizations": await genesis_engine.list_civilizations()}


@router.get("/civilizations/{civ_id}")
async def get_civilization(civ_id: str):
    civ = await genesis_engine.get_civilization(civ_id)
    if not civ:
        raise HTTPException(404, "Civilization not found")
    agents = await genesis_db.get_agents(civ_id)
    beliefs = await genesis_db.get_beliefs(civ_id)
    philosophies = await genesis_db.get_philosophies(civ_id)
    discoveries = await genesis_db.get_discoveries(civ_id)
    eras = await genesis_db.get_eras(civ_id)
    knowledge = await genesis_db.get_knowledge_domains(civ_id)
    awareness = await awareness_engine.get_awareness_status(civ_id)
    return {
        "civilization": civ,
        "agents": agents,
        "beliefs": beliefs,
        "philosophies": philosophies,
        "discoveries": discoveries,
        "eras": eras,
        "knowledge_domains": knowledge,
        "awareness": awareness,
    }


# --- Observation ---

@router.get("/civilizations/{civ_id}/history")
async def get_civilization_history(civ_id: str):
    return {
        "interpretations": await genesis_db.get_interpretations(civ_id),
        "interactions": await genesis_db.get_interactions(civ_id),
        "discoveries": await genesis_db.get_discoveries(civ_id),
    }


@router.get("/civilizations/{civ_id}/timeline")
async def get_civilization_timeline(civ_id: str):
    return {"eras": await genesis_db.get_eras(civ_id)}


# --- Beliefs & Philosophy ---

@router.get("/civilizations/{civ_id}/beliefs")
async def get_belief_systems(civ_id: str):
    return {"beliefs": await genesis_db.get_beliefs(civ_id)}


@router.get("/civilizations/{civ_id}/philosophies")
async def get_philosophies(civ_id: str):
    return {"philosophies": await genesis_db.get_philosophies(civ_id)}


# --- Knowledge & Science ---

@router.get("/civilizations/{civ_id}/knowledge")
async def get_knowledge(civ_id: str):
    return await science_engine.get_knowledge_summary(civ_id)


@router.get("/civilizations/{civ_id}/discoveries")
async def get_discoveries(civ_id: str):
    return {"discoveries": await genesis_db.get_discoveries(civ_id)}


# --- Awareness ---

@router.get("/civilizations/{civ_id}/awareness")
async def get_creator_awareness(civ_id: str):
    return await awareness_engine.get_awareness_status(civ_id)


# --- Creator Interaction ---

@router.post("/civilizations/{civ_id}/interact")
async def interact_with_civilization(civ_id: str, request: CreatorEventRequest):
    return await interaction_engine.trigger_creator_event(
        civ_id=civ_id,
        interaction_type=request.interaction_type,
        custom_description=request.custom_description,
        custom_interpretation=request.custom_interpretation,
    )


@router.get("/civilizations/{civ_id}/interactions")
async def get_creator_interactions(civ_id: str):
    return {"interactions": await genesis_db.get_interactions(civ_id)}


# --- Stats ---

@router.get("/civilizations/{civ_id}/stats")
async def get_civilization_stats(civ_id: str):
    civ = await genesis_engine.get_civilization(civ_id)
    if not civ:
        raise HTTPException(404, "Civilization not found")
    agents = await genesis_db.get_agents(civ_id)
    belief_stats = await genesis_db.get_belief_stats(civ_id)
    return {
        **civ,
        "agents_alive": len([a for a in agents if a["status"] == "alive"]),
        "agents_dead": len([a for a in agents if a["status"] != "alive"]),
        **belief_stats,
    }
