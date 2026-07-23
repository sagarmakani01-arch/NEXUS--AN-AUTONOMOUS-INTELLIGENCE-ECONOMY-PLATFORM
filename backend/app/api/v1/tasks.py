from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.domain.models.user import User
from app.domain.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(
    data: TaskCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.create_task(user.id, data)


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 50,
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.list_tasks(skip, limit)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.get_task(task_id)


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    data: TaskUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    return await service.update_task(task_id, data)


@router.delete("/{task_id}")
async def delete_task(
    task_id: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    service = TaskService(session)
    await service.delete_task(task_id)
    return {"detail": "Task deleted"}
