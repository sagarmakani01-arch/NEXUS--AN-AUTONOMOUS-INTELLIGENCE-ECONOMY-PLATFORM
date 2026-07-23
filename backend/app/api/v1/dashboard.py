from fastapi import APIRouter
from pydantic import BaseModel

from app.simulation.engine import engine

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


class DashboardStats(BaseModel):
    total_agents: int
    active_agents: int
    active_tasks: int
    total_users: int
    total_companies: int
    total_transactions: int
    economy_status: str
    compute_usage: str
    simulation_status: str
    world_time: str | None = None
    simulation_speed: int = 1
    avg_energy: float = 0
    avg_reputation: float = 0
    working_agents: int = 0
    idle_agents: int = 0
    searching_agents: int = 0
    resting_agents: int = 0
    events_per_second: float = 0
    population: int = 0


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    s = engine.world.state
    return DashboardStats(
        total_agents=len(engine.agents),
        active_agents=len([a for a in engine.agents if a.current_status != "resting"]),
        active_tasks=0,
        total_users=0,
        total_companies=0,
        total_transactions=0,
        economy_status="simulated" if engine.state.value == "running" else engine.state.value,
        compute_usage="active" if engine.state.value == "running" else "idle",
        simulation_status=engine.state.value,
        world_time=s.clock.time_str,
        simulation_speed=engine.speed.value,
        avg_energy=s.avg_energy,
        avg_reputation=s.avg_reputation,
        working_agents=s.working_agents,
        idle_agents=s.idle_agents,
        searching_agents=s.searching_agents,
        resting_agents=s.resting_agents,
        events_per_second=s.events_per_second,
        population=s.population,
    )
