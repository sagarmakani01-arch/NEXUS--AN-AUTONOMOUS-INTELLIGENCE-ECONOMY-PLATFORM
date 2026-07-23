from datetime import datetime

from pydantic import BaseModel, field_validator


class AgentCreate(BaseModel):
    name: str
    profession_id: str | None = None
    personality_profile: dict = {}
    current_goal: str | None = None


class AgentUpdate(BaseModel):
    name: str | None = None
    profession_id: str | None = None
    personality_profile: dict | None = None
    current_goal: str | None = None
    current_status: str | None = None
    energy: int | None = None


class AgentResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    profession_id: str | None
    personality_profile: dict = {}
    reputation: float
    current_goal: str | None
    current_status: str
    energy: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_validator("personality_profile", mode="before")
    @classmethod
    def parse_personality(cls, v):
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except (json.JSONDecodeError, TypeError):
                return {}


class AgentDetailResponse(AgentResponse):
    skills: list["SkillResponse"] = []
    wallet: "WalletResponse | None" = None


class SkillResponse(BaseModel):
    id: str
    name: str
    category: str | None
    description: str | None
    proficiency_levels: int

    model_config = {"from_attributes": True}


class SkillCreate(BaseModel):
    name: str
    category: str | None = None
    description: str | None = None
    proficiency_levels: int = 5


class WalletResponse(BaseModel):
    id: str
    agent_id: str
    balance: float
    currency: str
    status: str

    model_config = {"from_attributes": True}
