from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.domain.models.user import User
from app.domain.schemas.user import UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(data: UserCreate, session: AsyncSession = Depends(get_db)):
    service = AuthService(session)
    return await service.register(data)


@router.post("/login")
async def login(data: UserLogin, session: AsyncSession = Depends(get_db)):
    service = AuthService(session)
    return await service.login(data)


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse.model_validate(user)
