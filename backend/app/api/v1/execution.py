from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.domain.models.user import User
from app.execution import (
    capability_system,
    collaboration,
    execution_engine,
    goal_decomposition,
    learning,
    orchestrator,
    quality_evaluation,
    tool_system,
    work_environment,
)

router = APIRouter(prefix="/execution", tags=["Execution"])


class ProjectCreateRequest(BaseModel):
    title: str
    description: str = ""
    goal: str = ""
    priority: str = "medium"
    estimated_cost: float = 0


class GoalExecuteRequest(BaseModel):
    agent_id: str
    goal: str
    title: str = ""


class TeamCreateRequest(BaseModel):
    project_id: str
    agent_ids: list[str]
    roles: dict[str, str] | None = None


class ToolExecuteRequest(BaseModel):
    tool_name: str
    agent_id: str
    params: dict = {}


@router.get("/stats")
async def execution_stats():
    return await execution_engine.get_full_state()


@router.post("/projects")
async def create_project(data: ProjectCreateRequest, user: User = Depends(get_current_user)):
    agent_id = user.id
    from app.simulation.engine import engine as sim_engine
    idle_agents = [a for a in sim_engine.agents if a.current_status == "idle"]
    if idle_agents:
        agent_id = idle_agents[0].id
    return await execution_engine.create_project(
        agent_id=agent_id, title=data.title,
        description=data.description, goal=data.goal or data.title,
        priority=data.priority, estimated_cost=data.estimated_cost,
    )


@router.get("/projects")
async def list_projects(agent_id: str = "", status: str = ""):
    return await execution_engine.list_projects(agent_id=agent_id, status=status)


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await execution_engine.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects/{project_id}/start")
async def start_project(project_id: str):
    result = await execution_engine.start_project(project_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/projects/{project_id}/pause")
async def pause_project(project_id: str):
    return await execution_engine.pause_project(project_id)


@router.post("/projects/{project_id}/resume")
async def resume_project(project_id: str):
    return await execution_engine.resume_project(project_id)


@router.post("/execute")
async def execute_goal(data: GoalExecuteRequest):
    return await execution_engine.execute_goal(data.agent_id, data.goal, data.title)


@router.get("/tasks")
async def list_tasks(project_id: str = "", status: str = "", agent_id: str = ""):
    from app.execution.persistence import list_execution_tasks
    return await list_execution_tasks(project_id=project_id, status=status, agent_id=agent_id)


@router.get("/tasks/{task_id}")
async def get_task(task_id: str):
    from app.execution.persistence import get_execution_task
    task = await get_execution_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/tasks/ready/{project_id}")
async def get_ready_tasks(project_id: str):
    return await goal_decomposition.get_ready_tasks(project_id)


@router.get("/cost-estimate/{project_id}")
async def cost_estimate(project_id: str):
    return await goal_decomposition.estimate_project_cost(project_id)


@router.get("/tools")
async def list_tools(tool_type: str = ""):
    return await tool_system.list_tools(tool_type=tool_type)


@router.post("/tools/execute")
async def execute_tool(data: ToolExecuteRequest):
    result = await tool_system.execute_tool(data.tool_name, data.agent_id, data.params)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/capabilities/{agent_id}")
async def get_capabilities(agent_id: str):
    return await capability_system.get_agent_profile(agent_id)


@router.post("/collaborate/team")
async def create_team(data: TeamCreateRequest):
    return await collaboration.create_team(data.project_id, data.agent_ids, data.roles)


@router.get("/quality/{project_id}")
async def project_quality(project_id: str):
    return await quality_evaluation.evaluate_project(project_id)


@router.get("/learning/{agent_id}")
async def agent_learning(agent_id: str):
    return await learning.get_agent_learning_stats(agent_id)


@router.get("/workspaces/{agent_id}")
async def agent_workspaces(agent_id: str):
    return await work_environment.list_agent_workspaces(agent_id)


@router.get("/workspaces/detail/{workspace_id}")
async def workspace_detail(workspace_id: str):
    ws = await work_environment.get_workspace(workspace_id)
    if not ws:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return ws
