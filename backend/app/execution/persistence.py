from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.domain.models.agent_capability import AgentCapability
from app.domain.models.execution_result import ExecutionResult
from app.domain.models.execution_task import ExecutionTask
from app.domain.models.project import Project
from app.domain.models.tool import Tool
from app.domain.models.workspace import Workspace

logger = logging.getLogger("nexus.execution")


async def create_project(
    agent_id: str, title: str, description: str = "",
    contract_id: str | None = None, priority: str = "medium",
    estimated_cost: float = 0, metadata_json: str = "{}",
) -> dict:
    async with async_session_factory() as session:
        project = Project(
            agent_id=agent_id, title=title, description=description,
            contract_id=contract_id, priority=priority,
            estimated_cost=estimated_cost, metadata_json=metadata_json,
        )
        session.add(project)
        await session.commit()
        await session.refresh(project)
        return _project_to_dict(project)


async def get_project(project_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        return _project_to_dict(project) if project else None


async def list_projects(agent_id: str = "", status: str = "", skip: int = 0, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        q = select(Project)
        if agent_id:
            q = q.where(Project.agent_id == agent_id)
        if status:
            q = q.where(Project.status == status)
        q = q.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(q)
        return [_project_to_dict(p) for p in result.scalars().all()]


async def update_project(project_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(project, k):
                setattr(project, k, v)
        await session.commit()
        await session.refresh(project)
        return _project_to_dict(project)


async def create_execution_task(
    project_id: str, title: str, description: str = "",
    required_skills: list[str] | None = None, priority: str = "medium",
    dependencies: list[str] | None = None, estimated_cost: float = 0,
    estimated_duration: int = 0, parent_task_id: str | None = None,
) -> dict:
    async with async_session_factory() as session:
        task = ExecutionTask(
            project_id=project_id, title=title, description=description,
            required_skills=json.dumps(required_skills or []),
            priority=priority, dependencies=json.dumps(dependencies or []),
            estimated_cost=estimated_cost, estimated_duration=estimated_duration,
            parent_task_id=parent_task_id,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return _task_to_dict(task)


async def get_execution_task(task_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(ExecutionTask).where(ExecutionTask.id == task_id))
        task = result.scalar_one_or_none()
        return _task_to_dict(task) if task else None


async def list_execution_tasks(project_id: str = "", status: str = "", agent_id: str = "", skip: int = 0, limit: int = 100) -> list[dict]:
    async with async_session_factory() as session:
        q = select(ExecutionTask)
        if project_id:
            q = q.where(ExecutionTask.project_id == project_id)
        if status:
            q = q.where(ExecutionTask.status == status)
        if agent_id:
            q = q.where(ExecutionTask.agent_id == agent_id)
        q = q.order_by(ExecutionTask.created_at.desc()).offset(skip).limit(limit)
        result = await session.execute(q)
        return [_task_to_dict(t) for t in result.scalars().all()]


async def update_execution_task(task_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(ExecutionTask).where(ExecutionTask.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(task, k):
                setattr(task, k, v)
        await session.commit()
        await session.refresh(task)
        return _task_to_dict(task)


async def create_tool(
    name: str, description: str = "", tool_type: str = "utility",
    required_permission: str = "basic", cost_per_use: float = 0,
    input_schema: str = "{}", output_schema: str = "{}",
) -> dict:
    async with async_session_factory() as session:
        tool = Tool(
            name=name, description=description, tool_type=tool_type,
            required_permission=required_permission, cost_per_use=cost_per_use,
            input_schema=input_schema, output_schema=output_schema,
        )
        session.add(tool)
        await session.commit()
        await session.refresh(tool)
        return _tool_to_dict(tool)


async def get_tool(tool_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Tool).where(Tool.id == tool_id))
        tool = result.scalar_one_or_none()
        return _tool_to_dict(tool) if tool else None


async def list_tools(tool_type: str = "", status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        q = select(Tool)
        if tool_type:
            q = q.where(Tool.tool_type == tool_type)
        if status:
            q = q.where(Tool.status == status)
        q = q.order_by(Tool.name)
        result = await session.execute(q)
        return [_tool_to_dict(t) for t in result.scalars().all()]


async def update_tool(tool_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Tool).where(Tool.id == tool_id))
        tool = result.scalar_one_or_none()
        if not tool:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(tool, k):
                setattr(tool, k, v)
        await session.commit()
        await session.refresh(tool)
        return _tool_to_dict(tool)


async def create_capability(
    agent_id: str, skill_name: str, level: str = "beginner",
    proficiency: float = 0.0,
) -> dict:
    async with async_session_factory() as session:
        cap = AgentCapability(
            agent_id=agent_id, skill_name=skill_name,
            level=level, proficiency=proficiency,
        )
        session.add(cap)
        await session.commit()
        await session.refresh(cap)
        return _capability_to_dict(cap)


async def get_capabilities(agent_id: str) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(AgentCapability).where(AgentCapability.agent_id == agent_id)
        )
        return [_capability_to_dict(c) for c in result.scalars().all()]


async def update_capability(cap_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(AgentCapability).where(AgentCapability.id == cap_id))
        cap = result.scalar_one_or_none()
        if not cap:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(cap, k):
                setattr(cap, k, v)
        await session.commit()
        await session.refresh(cap)
        return _capability_to_dict(cap)


async def create_workspace(
    agent_id: str, name: str, project_id: str | None = None,
    description: str = "",
) -> dict:
    async with async_session_factory() as session:
        ws = Workspace(
            agent_id=agent_id, name=name, project_id=project_id,
            description=description,
        )
        session.add(ws)
        await session.commit()
        await session.refresh(ws)
        return _workspace_to_dict(ws)


async def get_workspace(workspace_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Workspace).where(Workspace.id == workspace_id))
        ws = result.scalar_one_or_none()
        return _workspace_to_dict(ws) if ws else None


async def list_workspaces(agent_id: str = "") -> list[dict]:
    async with async_session_factory() as session:
        q = select(Workspace)
        if agent_id:
            q = q.where(Workspace.agent_id == agent_id)
        q = q.order_by(Workspace.created_at.desc())
        result = await session.execute(q)
        return [_workspace_to_dict(w) for w in result.scalars().all()]


async def update_workspace(workspace_id: str, **kwargs) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Workspace).where(Workspace.id == workspace_id))
        ws = result.scalar_one_or_none()
        if not ws:
            return None
        for k, v in kwargs.items():
            if v is not None and hasattr(ws, k):
                setattr(ws, k, v)
        await session.commit()
        await session.refresh(ws)
        return _workspace_to_dict(ws)


async def create_execution_result(
    task_id: str, agent_id: str, project_id: str,
    status: str, quality_score: float = 0,
    requirements_met: float = 0, errors_count: float = 0,
    efficiency_score: float = 0, user_satisfaction: float = 0,
    deliverables: list[str] | None = None, feedback: str = "",
    lessons_learned: list[str] | None = None, tools_used: list[str] | None = None,
    duration_seconds: float = 0, cost_incurred: float = 0,
) -> dict:
    async with async_session_factory() as session:
        result = ExecutionResult(
            task_id=task_id, agent_id=agent_id, project_id=project_id,
            status=status, quality_score=quality_score,
            requirements_met=requirements_met, errors_count=errors_count,
            efficiency_score=efficiency_score, user_satisfaction=user_satisfaction,
            deliverables=json.dumps(deliverables or []),
            feedback=feedback,
            lessons_learned=json.dumps(lessons_learned or []),
            tools_used=json.dumps(tools_used or []),
            duration_seconds=duration_seconds, cost_incurred=cost_incurred,
        )
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return _result_to_dict(result)


async def list_execution_results(project_id: str = "", agent_id: str = "") -> list[dict]:
    async with async_session_factory() as session:
        q = select(ExecutionResult)
        if project_id:
            q = q.where(ExecutionResult.project_id == project_id)
        if agent_id:
            q = q.where(ExecutionResult.agent_id == agent_id)
        q = q.order_by(ExecutionResult.created_at.desc()).limit(100)
        result = await session.execute(q)
        return [_result_to_dict(r) for r in result.scalars().all()]


async def get_execution_stats() -> dict:
    async with async_session_factory() as session:
        project_counts = await session.execute(
            select(Project.status, func.count()).group_by(Project.status)
        )
        projects = {row[0]: row[1] for row in project_counts.all()}

        task_counts = await session.execute(
            select(ExecutionTask.status, func.count()).group_by(ExecutionTask.status)
        )
        tasks = {row[0]: row[1] for row in task_counts.all()}

        avg_quality = await session.execute(
            select(func.avg(ExecutionResult.quality_score))
        )
        avg_q = avg_quality.scalar_one() or 0

        total_completed = await session.execute(
            select(func.count()).select_from(ExecutionResult).where(ExecutionResult.status == "completed")
        )
        total_all = await session.execute(select(func.count()).select_from(ExecutionResult))

        completed = total_completed.scalar_one() or 0
        total = total_all.scalar_one() or 0

        return {
            "projects": projects,
            "tasks": tasks,
            "total_projects": sum(projects.values()),
            "total_tasks": sum(tasks.values()),
            "avg_quality_score": round(float(avg_q), 2),
            "completion_rate": round(completed / max(total, 1) * 100, 1),
            "total_results": total,
        }


def _project_to_dict(project: Project) -> dict:
    return {
        "id": project.id,
        "agent_id": project.agent_id,
        "contract_id": project.contract_id,
        "title": project.title,
        "description": project.description,
        "status": project.status,
        "priority": project.priority,
        "total_tasks": project.total_tasks,
        "completed_tasks": project.completed_tasks,
        "failed_tasks": project.failed_tasks,
        "progress": project.progress,
        "estimated_cost": project.estimated_cost,
        "actual_cost": project.actual_cost,
        "quality_score": project.quality_score,
        "metadata_json": project.metadata_json,
        "created_at": project.created_at.isoformat() if project.created_at else None,
        "updated_at": project.updated_at.isoformat() if project.updated_at else None,
        "completed_at": project.completed_at.isoformat() if project.completed_at else None,
    }


def _task_to_dict(task: ExecutionTask) -> dict:
    skills = task.required_skills
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except (json.JSONDecodeError, TypeError):
            skills = []
    deps = task.dependencies
    if isinstance(deps, str):
        try:
            deps = json.loads(deps)
        except (json.JSONDecodeError, TypeError):
            deps = []
    return {
        "id": task.id,
        "project_id": task.project_id,
        "parent_task_id": task.parent_task_id,
        "agent_id": task.agent_id,
        "title": task.title,
        "description": task.description,
        "required_skills": skills,
        "status": task.status,
        "priority": task.priority,
        "dependencies": deps,
        "estimated_cost": task.estimated_cost,
        "actual_cost": task.actual_cost,
        "estimated_duration": task.estimated_duration,
        "actual_duration": task.actual_duration,
        "retry_count": task.retry_count,
        "max_retries": task.max_retries,
        "quality_score": task.quality_score,
        "result": task.result,
        "error_message": task.error_message,
        "metadata_json": task.metadata_json,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
    }


def _tool_to_dict(tool: Tool) -> dict:
    return {
        "id": tool.id,
        "name": tool.name,
        "description": tool.description,
        "tool_type": tool.tool_type,
        "required_permission": tool.required_permission,
        "cost_per_use": tool.cost_per_use,
        "input_schema": tool.input_schema,
        "output_schema": tool.output_schema,
        "status": tool.status,
        "total_uses": tool.total_uses,
        "avg_execution_time": tool.avg_execution_time,
        "success_rate": tool.success_rate,
        "metadata_json": tool.metadata_json,
        "created_at": tool.created_at.isoformat() if tool.created_at else None,
        "updated_at": tool.updated_at.isoformat() if tool.updated_at else None,
    }


def _capability_to_dict(cap: AgentCapability) -> dict:
    return {
        "id": cap.id,
        "agent_id": cap.agent_id,
        "skill_name": cap.skill_name,
        "level": cap.level,
        "proficiency": cap.proficiency,
        "experience": cap.experience,
        "projects_completed": cap.projects_completed,
        "success_rate": cap.success_rate,
        "last_used": cap.last_used.isoformat() if cap.last_used else None,
        "metadata_json": cap.metadata_json,
        "created_at": cap.created_at.isoformat() if cap.created_at else None,
        "updated_at": cap.updated_at.isoformat() if cap.updated_at else None,
    }


def _workspace_to_dict(ws: Workspace) -> dict:
    files = ws.files_json
    if isinstance(files, str):
        try:
            files = json.loads(files)
        except (json.JSONDecodeError, TypeError):
            files = []
    artifacts = ws.artifacts_json
    if isinstance(artifacts, str):
        try:
            artifacts = json.loads(artifacts)
        except (json.JSONDecodeError, TypeError):
            artifacts = []
    history = ws.task_history_json
    if isinstance(history, str):
        try:
            history = json.loads(history)
        except (json.JSONDecodeError, TypeError):
            history = []
    return {
        "id": ws.id,
        "agent_id": ws.agent_id,
        "project_id": ws.project_id,
        "name": ws.name,
        "description": ws.description,
        "files": files,
        "notes": ws.notes,
        "artifacts": artifacts,
        "task_history": history,
        "status": ws.status,
        "created_at": ws.created_at.isoformat() if ws.created_at else None,
        "updated_at": ws.updated_at.isoformat() if ws.updated_at else None,
    }


def _result_to_dict(result: ExecutionResult) -> dict:
    deliverables = result.deliverables
    if isinstance(deliverables, str):
        try:
            deliverables = json.loads(deliverables)
        except (json.JSONDecodeError, TypeError):
            deliverables = []
    lessons = result.lessons_learned
    if isinstance(lessons, str):
        try:
            lessons = json.loads(lessons)
        except (json.JSONDecodeError, TypeError):
            lessons = []
    tools = result.tools_used
    if isinstance(tools, str):
        try:
            tools = json.loads(tools)
        except (json.JSONDecodeError, TypeError):
            tools = []
    return {
        "id": result.id,
        "task_id": result.task_id,
        "agent_id": result.agent_id,
        "project_id": result.project_id,
        "status": result.status,
        "quality_score": result.quality_score,
        "requirements_met": result.requirements_met,
        "errors_count": result.errors_count,
        "efficiency_score": result.efficiency_score,
        "user_satisfaction": result.user_satisfaction,
        "deliverables": deliverables,
        "feedback": result.feedback,
        "lessons_learned": lessons,
        "tools_used": tools,
        "duration_seconds": result.duration_seconds,
        "cost_incurred": result.cost_incurred,
        "metadata_json": result.metadata_json,
        "created_at": result.created_at.isoformat() if result.created_at else None,
    }
