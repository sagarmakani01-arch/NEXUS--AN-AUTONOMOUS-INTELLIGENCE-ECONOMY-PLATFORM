from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import Event, EventType, dispatch
from app.core.security import create_access_token, hash_password, verify_password
from app.domain.schemas.user import UserCreate, UserLogin, UserResponse
from app.repositories.user_repo import UserRepository


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = UserRepository(session)

    async def register(self, data: UserCreate) -> dict:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        if await self.repo.get_by_username(data.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

        user = await self.repo.create(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
        )

        await dispatch(Event(EventType.USER_REGISTERED, {"user_id": user.id, "email": user.email}))

        token = create_access_token(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }

    async def login(self, data: UserLogin) -> dict:
        user = await self.repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        token = create_access_token(user.id)
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": UserResponse.model_validate(user),
        }

    async def get_profile(self, user_id: str) -> UserResponse:
        user = await self.repo.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return UserResponse.model_validate(user)
