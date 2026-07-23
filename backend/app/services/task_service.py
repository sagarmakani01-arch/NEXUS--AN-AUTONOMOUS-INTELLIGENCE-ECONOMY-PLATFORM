from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.event_bus import Event, EventType, dispatch
from app.domain.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.repositories.task_repo import TaskRepository


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = TaskRepository(session)

    async def create_task(self, user_id: str, data: TaskCreate) -> TaskResponse:
        import json

        task = await self.repo.create(
            posted_by=user_id,
            title=data.title,
            description=data.description,
            required_skills=json.dumps(data.required_skills),
            reward=data.reward,
            priority=data.priority,
            deadline=data.deadline,
        )
        await dispatch(Event(EventType.TASK_POSTED, {"task_id": task.id, "title": task.title}))
        return TaskResponse.model_validate(task)

    async def get_task(self, task_id: str) -> TaskResponse:
        task = await self.repo.get(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return TaskResponse.model_validate(task)

    async def list_tasks(self, skip: int = 0, limit: int = 50) -> list[TaskResponse]:
        tasks = await self.repo.get_multi(skip, limit)
        return [TaskResponse.model_validate(t) for t in tasks]

    async def update_task(self, task_id: str, data: TaskUpdate) -> TaskResponse:
        import json

        task = await self.repo.get(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        update_data = data.model_dump(exclude_unset=True)
        if "required_skills" in update_data and update_data["required_skills"] is not None:
            update_data["required_skills"] = json.dumps(update_data["required_skills"])
        updated = await self.repo.update(task_id, **update_data)

        if update_data.get("status") == "completed":
            await dispatch(Event(EventType.TASK_COMPLETED, {"task_id": task_id}))
        else:
            await dispatch(Event(EventType.TASK_UPDATED, {"task_id": task_id, "changes": update_data}))

        return TaskResponse.model_validate(updated)

    async def delete_task(self, task_id: str) -> bool:
        task = await self.repo.get(task_id)
        if not task:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return await self.repo.delete(task_id)

    async def count_active_tasks(self) -> int:
        from sqlalchemy import func, select

        from app.domain.models.task import Task

        result = await self.repo.session.execute(
            select(func.count()).select_from(Task).where(Task.status.in_(["open", "in_progress"]))
        )
        return result.scalar_one()
