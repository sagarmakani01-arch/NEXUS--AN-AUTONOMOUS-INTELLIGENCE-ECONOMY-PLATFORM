from datetime import datetime

from pydantic import BaseModel, field_validator


class CompanyCreate(BaseModel):
    name: str
    description: str | None = None
    industry: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    industry: str | None = None


class CompanyResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    description: str | None
    industry: str | None
    treasury_balance: float
    status: str
    member_agent_ids: list = []
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("member_agent_ids", mode="before")
    @classmethod
    def parse_members(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []
