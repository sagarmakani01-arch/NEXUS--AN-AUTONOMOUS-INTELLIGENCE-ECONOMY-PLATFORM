from fastapi import APIRouter, HTTPException, Query

from app.planetary.engine import planetary_engine
from app.planetary import persistence as db
from app.planetary import planet as planet_gen
from app.planetary import climate as climate_engine
from app.planetary import resources as resources_engine
from app.planetary import infrastructure as infra_engine
from app.planetary import settlements as settlement_engine
from app.planetary import events as event_engine
from app.planetary import sustainability as sustain_engine

router = APIRouter(prefix="/api/v1/planetary", tags=["planetary"])


@router.get("/engine/state")
async def get_engine_state():
    return planetary_engine.get_state()

@router.post("/engine/start")
async def start_engine():
    await planetary_engine.start()
    return {"status": "started"}

@router.post("/engine/stop")
async def stop_engine():
    await planetary_engine.stop()
    return {"status": "stopped"}


@router.get("/planets")
async def list_planets():
    return await db.list_planets()

@router.get("/planets/{planet_id}")
async def get_planet(planet_id: str):
    result = await db.get_planet(planet_id)
    if not result:
        raise HTTPException(status_code=404, detail="Planet not found")
    return result

@router.post("/planets/generate")
async def generate_planet(name: str = "New World", seed: int = 99, region_count: int = 16):
    return await planet_gen.generate_planet(name, seed, region_count)


@router.get("/regions/{planet_id}")
async def list_regions(planet_id: str, terrain_type: str | None = None):
    return await db.list_regions(planet_id, terrain_type=terrain_type)

@router.get("/regions/detail/{region_id}")
async def get_region(region_id: str):
    result = await db.get_region(region_id)
    if not result:
        raise HTTPException(status_code=404, detail="Region not found")
    return result


@router.get("/climate/{planet_id}")
async def list_climate(planet_id: str, region_id: str | None = None):
    return await db.list_climate_records(planet_id, region_id=region_id)

@router.post("/climate/evolve")
async def evolve_climate(planet_id: str):
    return await climate_engine.evolve_climate(planet_id)


@router.get("/resources/{planet_id}")
async def list_resources(planet_id: str, region_id: str | None = None,
                         resource_type: str | None = None):
    return await db.list_resources(planet_id, region_id=region_id, resource_type=resource_type)

@router.post("/resources/extract")
async def extract_resource(resource_id: str, amount: float = 10.0):
    result = await resources_engine.extract_resource(resource_id, amount)
    if not result:
        raise HTTPException(status_code=404, detail="Resource not found")
    return result

@router.post("/resources/survey")
async def survey_resources(planet_id: str, region_id: str):
    return await resources_engine.survey_resources(planet_id, region_id)


@router.get("/infrastructure/{planet_id}")
async def list_infrastructure(planet_id: str, region_id: str | None = None,
                              civilization_id: str | None = None):
    return await db.list_infrastructure(planet_id, region_id=region_id, civilization_id=civilization_id)

@router.post("/infrastructure/build")
async def build_infrastructure(planet_id: str, region_id: str, civilization_id: str,
                               infra_type: str, name: str | None = None):
    return await infra_engine.build_infrastructure(planet_id, region_id, civilization_id, infra_type, name)

@router.post("/infrastructure/{infra_id}/upgrade")
async def upgrade_infrastructure(infra_id: str):
    result = await infra_engine.upgrade_infrastructure(infra_id)
    if not result:
        raise HTTPException(status_code=404, detail="Infrastructure not found")
    return result


@router.get("/settlements/{planet_id}")
async def list_settlements(planet_id: str, civilization_id: str | None = None):
    return await db.list_settlements(planet_id, civilization_id=civilization_id)

@router.get("/settlements/detail/{settlement_id}")
async def get_settlement(settlement_id: str):
    result = await db.get_settlement(settlement_id)
    if not result:
        raise HTTPException(status_code=404, detail="Settlement not found")
    return result

@router.post("/settlements/found")
async def found_settlement(planet_id: str, region_id: str, civilization_id: str, name: str):
    return await settlement_engine.found_settlement(planet_id, region_id, civilization_id, name)


@router.get("/events/{planet_id}")
async def list_events(planet_id: str, event_type: str | None = None,
                      status: str | None = None, limit: int = Query(ge=1, le=200, default=50)):
    return await db.list_env_events(planet_id, event_type=event_type, status=status, limit=limit)

@router.post("/events/trigger")
async def trigger_event(planet_id: str, event_type: str | None = None, region_id: str | None = None):
    return await event_engine.trigger_event(planet_id, event_type, region_id)


@router.get("/sustainability/{planet_id}")
async def list_sustainability(planet_id: str, civilization_id: str | None = None):
    return await db.list_sustainability(planet_id, civilization_id=civilization_id)

@router.post("/sustainability/calculate")
async def calculate_sustainability(planet_id: str, civilization_id: str):
    return await sustain_engine.calculate_sustainability(planet_id, civilization_id)


@router.get("/impacts/{planet_id}")
async def list_impacts(planet_id: str, civilization_id: str | None = None):
    return await db.list_impacts(planet_id, civilization_id=civilization_id)


@router.get("/stats")
async def get_stats():
    return await db.get_planet_stats()
