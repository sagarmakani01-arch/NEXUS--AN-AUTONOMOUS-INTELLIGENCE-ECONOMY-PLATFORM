from datetime import datetime

from pydantic import BaseModel, field_validator


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    required_skills: list[str] = []
    reward: int = 0
    priority: str = "medium"
    deadline: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    required_skills: list[str] | None = None
    reward: int | None = None
    status: str | None = None
    priority: str | None = None
    result: str | None = None


class TaskResponse(BaseModel):
    id: str
    posted_by: str
    title: str
    description: str | None
    required_skills: list = []
    reward: int
    status: str
    priority: str
    deadline: datetime | None
    result: str | None
    created_at: datetime
    updated_at: datetime

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
