from fastapi import APIRouter, HTTPException, Query

from app.federation.engine import federation_engine
from app.federation.civilizations import civilization_manager
from app.federation.diplomacy import diplomacy_engine
from app.federation.trade import trade_engine
from app.federation.knowledge import knowledge_exchange_engine
from app.federation.competition import competition_engine
from app.federation.migration import migration_engine
from app.federation.council import federation_council_manager
from app.federation.analytics import federation_analytics
from app.federation import persistence as db

router = APIRouter(prefix="/api/v1/federation", tags=["federation"])


@router.get("/engine/state")
async def get_engine_state():
    return federation_engine.get_state()

@router.post("/engine/start")
async def start_engine():
    await federation_engine.start()
    return {"status": "started"}

@router.post("/engine/stop")
async def stop_engine():
    await federation_engine.stop()
    return {"status": "stopped"}

@router.post("/engine/tick")
async def manual_tick():
    await federation_engine.tick()
    return {"status": "tick_completed"}


@router.get("/civilizations")
async def list_civilizations():
    return await civilization_manager.list_civilizations()

@router.get("/civilizations/{civ_id}")
async def get_civilization(civ_id: str):
    result = await civilization_manager.get_civilization(civ_id)
    if not result:
        raise HTTPException(status_code=404, detail="Civilization not found")
    return result

@router.post("/civilizations")
async def create_civilization(name: str | None = None,
                              government_type: str | None = None,
                              economic_model: str | None = None,
                              population: int = 100):
    return await civilization_manager.create_civilization(
        name=name, government_type=government_type,
        economic_model=economic_model, population=population)

@router.put("/civilizations/{civ_id}")
async def update_civilization(civ_id: str, **kwargs):
    return await civilization_manager.update_civilization(civ_id, **kwargs)


@router.get("/diplomacy")
async def list_relations(civ_id: str | None = None):
    return await diplomacy_engine.list_relations(civ_id)

@router.get("/diplomacy/{civ_a_id}/{civ_b_id}")
async def get_relation(civ_a_id: str, civ_b_id: str):
    result = await diplomacy_engine.get_relation(civ_a_id, civ_b_id)
    if not result:
        raise HTTPException(status_code=404, detail="No relation found")
    return result

@router.post("/diplomacy/establish")
async def establish_relation(civ_a_id: str, civ_b_id: str,
                             status: str = "neutral"):
    return await diplomacy_engine.establish_relation(civ_a_id, civ_b_id, status)

@router.post("/diplomacy/update")
async def update_relation(civ_a_id: str, civ_b_id: str, status: str):
    return await diplomacy_engine.update_relation(civ_a_id, civ_b_id, status)

@router.post("/diplomacy/action")
async def diplomatic_action(civ_a_id: str, civ_b_id: str, action: str):
    return await diplomacy_engine.conduct_action(civ_a_id, civ_b_id, action)


@router.get("/trade")
async def list_trades(civ_id: str | None = None):
    return await trade_engine.list_trades(civ_id)

@router.post("/trade/create")
async def create_trade(civ_a_id: str, civ_b_id: str,
                       trade_type: str | None = None,
                       resource_offered: str | None = None,
                       resource_requested: str | None = None):
    return await trade_engine.create_trade(civ_a_id, civ_b_id, trade_type,
                                           resource_offered, resource_requested)


@router.get("/knowledge/messages")
async def get_messages(civ_id: str, limit: int = Query(ge=1, le=200, default=50)):
    return await knowledge_exchange_engine.get_messages(civ_id, limit)

@router.post("/knowledge/share")
async def share_knowledge(sender_civ_id: str, receiver_civ_id: str,
                          subject: str, content: str | None = None):
    return await knowledge_exchange_engine.share_knowledge(
        sender_civ_id, receiver_civ_id, subject, content)

@router.post("/knowledge/technology")
async def share_technology(sender_civ_id: str, receiver_civ_id: str,
                           tech_name: str):
    return await knowledge_exchange_engine.share_technology(
        sender_civ_id, receiver_civ_id, tech_name)


@router.post("/competition/run")
async def run_competition(civ_a_id: str, civ_b_id: str,
                          competition_type: str | None = None):
    return await competition_engine.run_competition(civ_a_id, civ_b_id, competition_type)

@router.get("/competition/rankings")
async def get_rankings():
    return await competition_engine.get_rankings()


@router.get("/migration")
async def list_migrations(civ_id: str | None = None):
    return await migration_engine.list_migrations(civ_id)

@router.post("/migration/process")
async def process_migration(agent_id: str, origin_civ_id: str,
                            destination_civ_id: str, reason: str | None = None):
    return await migration_engine.process_migration(
        agent_id, origin_civ_id, destination_civ_id, reason)

@router.get("/migration/pull/{civ_id}")
async def get_migration_pull(civ_id: str):
    return await migration_engine.evaluate_migration_pull(civ_id)


@router.get("/council")
async def list_councils():
    return await federation_council_manager.list_councils()

@router.get("/council/{council_id}")
async def get_council(council_id: str):
    result = await federation_council_manager.get_council(council_id)
    if not result:
        raise HTTPException(status_code=404, detail="Council not found")
    return result

@router.post("/council/create")
async def create_council(name: str, founding_civ_id: str,
                         description: str | None = None):
    return await federation_council_manager.create_council(name, founding_civ_id, description)

@router.post("/council/{council_id}/join")
async def join_council(council_id: str, civ_id: str):
    return await federation_council_manager.join_council(council_id, civ_id)


@router.get("/dashboard")
async def get_universe_dashboard():
    return await federation_analytics.get_universe_dashboard()

@router.get("/analytics/{civ_id}")
async def get_civilization_analytics(civ_id: str):
    return await federation_analytics.get_civilization_analytics(civ_id)

@router.get("/diplomacy/map")
async def get_diplomacy_map():
    return await federation_analytics.get_diplomacy_map()

@router.get("/stats")
async def get_federation_stats():
    return await db.get_federation_stats()

@router.get("/history/{civ_id}")
async def get_history(civ_id: str, limit: int = Query(ge=1, le=200, default=50)):
    return await db.get_history(civ_id, limit)
