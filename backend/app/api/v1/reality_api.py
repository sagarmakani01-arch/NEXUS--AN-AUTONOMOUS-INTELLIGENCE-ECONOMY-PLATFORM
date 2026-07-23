from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.reality.engine import reality_engine
from app.reality.world_generator import world_gen
from app.reality.entity_tracker import entity_tracker
from app.reality.cinematic_director import cinematic_director
from app.reality.interaction import interaction_handler
from app.reality.persistence import reality_db

router = APIRouter(prefix="/api/v1/reality", tags=["Reality"])


class InteractionQueryRequest(BaseModel):
    query: str
    target_type: Optional[str] = None
    target_id: Optional[str] = None


# --- State ---

@router.get("/state")
async def get_reality_state():
    return await reality_engine.get_full_state()


# --- Regions / World ---

@router.get("/regions")
async def list_regions():
    regions = await reality_db.get_regions()
    return {"regions": [{"id": r.id, "x": r.region_x, "z": r.region_z, "biome": r.biome, "buildings": r.building_count, "entities": r.entity_count} for r in regions]}


@router.get("/regions/{region_x}/{region_z}")
async def explore_region(region_x: int, region_z: int):
    region = await reality_engine.explore_region(region_x, region_z)
    if not region:
        raise HTTPException(404, "Region not found")
    return region


@router.get("/regions/nearby")
async def get_nearby_regions(x: int = Query(0), z: int = Query(0), radius: int = Query(2, ge=1, le=5)):
    return {"regions": await world_gen.get_nearby_regions(x, z, radius)}


# --- Buildings ---

@router.get("/buildings")
async def list_buildings(region_id: Optional[str] = None, building_type: Optional[str] = None):
    buildings = await reality_db.get_buildings(region_id, building_type)
    return {"buildings": [{"id": b.id, "type": b.building_type, "label": b.label, "x": b.pos_x, "z": b.pos_z, "color": b.color, "style": b.style, "occupants": b.occupants} for b in buildings]}


@router.get("/buildings/{building_id}")
async def get_building(building_id: str):
    b = await reality_db.get_building(building_id)
    if not b:
        raise HTTPException(404, "Building not found")
    return {"id": b.id, "type": b.building_type, "label": b.label, "x": b.pos_x, "y": b.pos_y, "z": b.pos_z, "w": b.width, "h": b.height, "d": b.depth, "color": b.color, "style": b.style, "occupants": b.occupants, "data": b.data}


# --- Entities / Citizens ---

@router.get("/entities")
async def list_entities(region_id: Optional[str] = None):
    return {"entities": await entity_tracker.get_entities_in_range(0, 0, 99999)}


@router.get("/entities/nearby")
async def get_nearby_entities(x: float = Query(0), z: float = Query(0), radius: float = Query(50)):
    return {"entities": await entity_tracker.get_entities_in_range(x, z, radius)}


@router.post("/entities/{agent_id}/update")
async def update_entity_position(agent_id: str, name: str = Query("Citizen"), x: float = Query(0), z: float = Query(0), activity: str = "idle"):
    return await entity_tracker.update_position(agent_id, name, x, z, activity)


@router.get("/entities/follow/{agent_id}")
async def follow_entity(agent_id: str):
    result = await entity_tracker.follow_entity(agent_id)
    if not result:
        raise HTTPException(404, "Entity not found")
    return result


# --- Cameras ---

@router.get("/cameras")
async def list_cameras():
    cameras = await reality_db.get_cameras()
    return {"cameras": [{"id": c.id, "name": c.name, "mode": c.mode, "x": c.cam_x, "y": c.cam_y, "z": c.cam_z} for c in cameras]}


@router.post("/cameras/save")
async def save_camera(name: str = Query(...), x: float = Query(0), y: float = Query(50), z: float = Query(0), mode: str = "free"):
    from app.domain.models.virtual import VirtualCameraState
    cam = VirtualCameraState(name=name, cam_x=x, cam_y=y, cam_z=z, mode=mode)
    saved = await reality_db.save_camera(cam)
    return {"id": saved.id, "name": saved.name, "mode": saved.mode}


# --- Cinematic ---

@router.get("/cinematic/events")
async def get_cinematic_events():
    return await cinematic_director.get_pending_events()


@router.post("/cinematic/generate")
async def generate_cinematic(event_type: Optional[str] = None):
    return await cinematic_director.generate_event(event_type)


@router.post("/cinematic/trigger/{event_id}")
async def trigger_cinematic(event_id: str):
    return await cinematic_director.trigger_event(event_id)


# --- Interaction ---

@router.post("/interact/query")
async def query_world(request: InteractionQueryRequest, user_id: str = Query("anonymous")):
    return await interaction_handler.handle_query(user_id, request.query, request.target_type, request.target_id)


@router.get("/interact/history")
async def get_interaction_history(user_id: str = Query("anonymous"), limit: int = Query(20)):
    return {"history": await interaction_handler.get_history(user_id, limit)}
