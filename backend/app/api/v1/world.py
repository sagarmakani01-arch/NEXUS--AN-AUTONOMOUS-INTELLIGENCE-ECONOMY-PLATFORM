from fastapi import APIRouter, HTTPException, Query

from app.world.state import world_state
from app.world.movement import citizen_movement_engine

router = APIRouter(prefix="/api/v1/world", tags=["world"])


@router.get("/state")
async def get_world_state():
    return world_state.get_full_state()


@router.get("/map")
async def get_map():
    return world_state.get_map_state()


@router.get("/buildings")
async def get_buildings(building_type: str | None = None, zone: str | None = None):
    buildings = world_state.buildings
    if building_type:
        buildings = [b for b in buildings if b.building_type == building_type]
    if zone:
        buildings = [b for b in buildings if b.zone == zone]
    return [b.to_dict() for b in buildings]


@router.get("/buildings/{building_id}")
async def get_building(building_id: str):
    building = next((b for b in world_state.buildings if b.id == building_id), None)
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building.to_dict()


@router.post("/buildings")
async def create_building(building_type: str, name: str, x: int, y: int):
    return world_state.add_building(building_type, name, x, y)


@router.get("/citizens")
async def get_citizens(visible_only: bool = True,
                       camera_x: float = 0, camera_y: float = 0,
                       view_width: float = 100, view_height: float = 100):
    return world_state.get_citizens_state(visible_only, camera_x, camera_y, view_width, view_height)


@router.get("/citizens/{agent_id}")
async def get_citizen_position(agent_id: str):
    pos = world_state.citizen_positions.get(agent_id)
    if not pos:
        raise HTTPException(status_code=404, detail="Citizen not found in world")
    return {"agent_id": agent_id, **pos}


@router.get("/events")
async def get_events(limit: int = Query(ge=1, le=200, default=50)):
    return world_state.get_events_state(limit)


@router.post("/events")
async def add_event(event_type: str, description: str,
                    x: float = 0, y: float = 0):
    world_state.add_event(event_type, description, x, y)
    return {"status": "added"}


@router.get("/time")
async def get_time():
    return world_state.get_time_state()


@router.post("/time/speed")
async def set_time_speed(speed: int = Query(ge=1, le=100)):
    world_state.time_state["speed"] = speed
    return {"speed": speed}


@router.post("/time/pause")
async def pause_time():
    world_state.time_state["paused"] = True
    return {"paused": True}


@router.post("/time/resume")
async def resume_time():
    world_state.time_state["paused"] = False
    return {"paused": False}


@router.get("/nearby")
async def get_nearby(x: float, y: float, radius: float = Query(ge=1, le=50, default=20)):
    return world_state.get_nearby_buildings(x, y, radius)


@router.get("/zones")
async def get_zones(zone_type: str | None = None):
    zones = world_state.zones
    if zone_type:
        zones = [z for z in zones if z.zone_type == zone_type]
    return [z.to_dict() for z in zones]


@router.get("/roads")
async def get_roads():
    return [r.to_dict() for r in world_state.roads]


@router.get("/movement/stats")
async def get_movement_stats():
    return citizen_movement_engine.get_state()


@router.post("/movement/initialize/{agent_id}")
async def initialize_citizen_movement(agent_id: str, name: str | None = None):
    await citizen_movement_engine.initialize_citizen(agent_id, name)
    return {"status": "initialized", "agent_id": agent_id}


@router.get("/overlay/population")
async def get_population_overlay():
    from collections import defaultdict
    grid = defaultdict(int)
    cell_size = 10
    for pos in world_state.citizen_positions.values():
        gx = int(pos["x"] // cell_size)
        gy = int(pos["y"] // cell_size)
        grid[f"{gx},{gy}"] += 1
    return [{"cell": k, "count": v} for k, v in grid.items()]


@router.get("/overlay/economic")
async def get_economic_overlay():
    zones = []
    for z in world_state.zones:
        building_count = len([b for b in world_state.buildings if b.zone == z.zone_type])
        zones.append({**z.to_dict(), "building_count": building_count,
                      "activity_score": building_count * 10 + len(world_state.citizen_positions) * 0.5})
    return zones
