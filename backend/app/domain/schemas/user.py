from datetime import datetime

from pydantic import BaseModel, field_validator


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    full_name: str | None
    role: str
    is_active: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
