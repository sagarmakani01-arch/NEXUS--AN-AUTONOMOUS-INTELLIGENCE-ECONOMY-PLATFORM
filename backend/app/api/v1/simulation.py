import asyncio
import json
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from app.simulation.engine import engine
from app.simulation.events import SimSpeed

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.get("/stream")
async def simulation_stream():
    async def event_generator():
        q = engine.subscribe_sse()
        try:
            yield f"data: {json.dumps(engine.get_full_state())}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=30)
                    yield f"data: {json.dumps(data)}\n\n"
                except asyncio.TimeoutError:
                    yield f"data: {json.dumps({'type': 'heartbeat', 'data': {}})}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            engine.unsubscribe_sse(q)

    return StreamingResponse(event_generator(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/state")
async def get_state():
    return engine.get_full_state()


@router.post("/start")
async def start_simulation():
    await engine.start()
    return {"status": "started", "state": engine.state.value}


@router.post("/pause")
async def pause_simulation():
    await engine.pause()
    return {"status": "paused", "state": engine.state.value}


@router.post("/reset")
async def reset_simulation():
    await engine.reset()
    return {"status": "reset", "state": engine.state.value}


@router.post("/speed")
async def set_speed(speed: int = Query(..., ge=1, le=100)):
    try:
        sim_speed = SimSpeed(speed)
    except ValueError:
        valid = [s.value for s in SimSpeed]
        return {"error": f"Invalid speed. Choose from: {valid}"}
    engine.set_speed(sim_speed)
    return {"status": "ok", "speed": sim_speed.value}


@router.get("/agents")
async def get_agents(page: int = Query(0, ge=0), size: int = Query(20, ge=1, le=100)):
    return engine.get_agents_page(page, size)


@router.get("/events")
async def get_events(limit: int = Query(50, ge=1, le=200)):
    return {"events": engine.event_queue.recent_events[-limit:]}
