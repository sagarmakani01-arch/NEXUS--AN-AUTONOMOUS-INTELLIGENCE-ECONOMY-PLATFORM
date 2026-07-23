from fastapi import APIRouter, HTTPException, Query

from app.technology.engine import technology_engine
from app.technology import persistence as db
from app.technology import graph as graph_engine
from app.technology import discovery as discovery_engine
from app.technology import development as development_engine
from app.technology import adoption as adoption_engine
from app.technology import organizations as org_engine
from app.technology import competition as competition_engine
from app.technology import obsolescence as obsolescence_engine
from app.technology import timeline as timeline_engine

router = APIRouter(prefix="/api/v1/technology", tags=["technology"])


@router.get("/engine/state")
async def get_engine_state():
    return technology_engine.get_state()

@router.post("/engine/start")
async def start_engine():
    await technology_engine.start()
    return {"status": "started"}

@router.post("/engine/stop")
async def stop_engine():
    await technology_engine.stop()
    return {"status": "stopped"}


@router.get("/graph")
async def list_graph(domain: str | None = None, status: str | None = None):
    return await db.list_technologies(domain=domain, status=status)

@router.get("/graph/{tech_id}")
async def get_technology(tech_id: str):
    result = await db.get_technology(tech_id)
    if not result:
        raise HTTPException(status_code=404, detail="Technology not found")
    return result

@router.post("/graph/create")
async def create_technology(name: str, domain: str, tech_type: str = "core",
                            description: str | None = None,
                            difficulty_level: float = 50.0, impact_score: float = 0.0):
    tid = await db.create_technology(
        name=name, domain=domain, tech_type=tech_type,
        description=description, difficulty_level=difficulty_level,
        impact_score=impact_score, status="concept",
    )
    techs = await db.list_technologies()
    return next((t for t in techs if t["id"] == tid), {})

@router.get("/graph/edges")
async def list_edges(source_id: str | None = None, target_id: str | None = None,
                    edge_type: str | None = None):
    return await db.list_technology_edges(source_id=source_id, target_id=target_id, edge_type=edge_type)


@router.post("/discovery/attempt")
async def attempt_discovery(civ_id: str, method: str = "research"):
    result = await discovery_engine.attempt_discovery(civ_id, method)
    return result or {"status": "no_discovery"}

@router.get("/discoveries")
async def list_discoveries(civ_id: str | None = None, limit: int = Query(ge=1, le=200, default=50)):
    return await db.list_discoveries(civ_id=civ_id, limit=limit)


@router.post("/development/start")
async def start_development(civ_id: str, tech_id: str, lead_agent_id: str | None = None):
    return await development_engine.start_development(civ_id, tech_id, lead_agent_id)

@router.post("/development/{dev_id}/advance")
async def advance_development(dev_id: str):
    result = await development_engine.advance_development(dev_id)
    if not result:
        raise HTTPException(status_code=404, detail="Development not found")
    return result

@router.get("/developments")
async def list_developments(civ_id: str | None = None, status: str | None = None):
    return await db.list_developments(civ_id=civ_id, status=status)


@router.post("/adoption/evaluate")
async def evaluate_adoption(civ_id: str, tech_id: str):
    return await adoption_engine.evaluate_adoption(civ_id, tech_id)

@router.get("/adoptions")
async def list_adoptions(civ_id: str | None = None, tech_id: str | None = None):
    return await db.list_adoptions(civ_id=civ_id, tech_id=tech_id)


@router.get("/organizations")
async def list_organizations(civ_id: str | None = None, org_type: str | None = None):
    return await db.list_scientific_organizations(civ_id=civ_id, org_type=org_type)

@router.post("/organizations/create")
async def create_organization(civ_id: str, name: str, org_type: str | None = None,
                              description: str | None = None):
    return await org_engine.create_organization(civ_id, name, org_type, description)


@router.get("/scientists")
async def list_scientists(civ_id: str | None = None, specialization: str | None = None):
    return await db.list_scientists(civ_id=civ_id, specialization=specialization)


@router.get("/tech-level/{civ_id}")
async def get_tech_level(civ_id: str):
    result = await db.get_tech_level(civ_id)
    if not result:
        raise HTTPException(status_code=404, detail="Tech level not found")
    return result


@router.get("/timeline/{civ_id}")
async def get_timeline(civ_id: str, limit: int = Query(ge=1, le=200, default=50)):
    return await timeline_engine.get_timeline(civ_id, limit)


@router.get("/era/{civ_id}")
async def get_era(civ_id: str):
    return {"era": await timeline_engine.get_era(civ_id)}


@router.get("/stats")
async def get_stats():
    return await db.get_tech_stats()
