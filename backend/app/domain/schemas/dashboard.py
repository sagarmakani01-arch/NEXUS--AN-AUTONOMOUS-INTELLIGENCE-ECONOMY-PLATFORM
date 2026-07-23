from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProfessionCreate(BaseModel):
    name: str
    description: str | None = None
    category: str | None = None


class ProfessionResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    category: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_agents: int
    active_agents: int
    active_tasks: int
    total_users: int
    total_companies: int
    total_transactions: int
    economy_status: str = "simulated"
    compute_usage: str = "placeholder"
    simulation_status: str = "idle"
