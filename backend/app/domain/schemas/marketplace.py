from datetime import datetime

from pydantic import BaseModel, field_validator


class ListingCreate(BaseModel):
    title: str
    description: str | None = None
    listing_type: str = "service"
    price: float = 0.0
    required_skills: list[str] = []


class ListingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = None
    status: str | None = None


class ListingResponse(BaseModel):
    id: str
    seller_agent_id: str
    title: str
    description: str | None
    listing_type: str
    price: float
    required_skills: list = []
    status: str
    quantity: int
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("required_skills", mode="before")
    @classmethod
    def parse_skills(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return []
        return v or []
