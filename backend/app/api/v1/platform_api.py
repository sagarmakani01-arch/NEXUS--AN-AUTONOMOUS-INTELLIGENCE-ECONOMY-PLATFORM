from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.platform.engine import platform_engine
from app.platform.plugins import plugin_system
from app.platform.sdk import sdk
from app.platform.modules import marketplace
from app.platform.templates import template_manager
from app.platform.scenarios import scenario_builder
from app.platform.workspace import workspace_manager
from app.platform.data_export import data_exporter
from app.platform.collaboration import collaboration

router = APIRouter(prefix="/api/v1/platform", tags=["Platform"])


class ScenarioCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    template_id: Optional[str] = None
    is_public: bool = True
    tags: Optional[list[str]] = None


class ExportRequest(BaseModel):
    name: str
    dataset_type: str
    format: str = "json"
    simulation_id: Optional[str] = None
    data: Optional[dict] = None


class WorkspaceCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    tags: Optional[list[str]] = None


# --- State ---

@router.get("/state")
async def get_platform_state():
    return await platform_engine.get_full_state()


# --- Plugins ---

@router.get("/plugins")
async def list_plugins(enabled: Optional[bool] = None):
    return {"plugins": await plugin_system.list_plugins(enabled)}


@router.post("/plugins/{plugin_id}/toggle")
async def toggle_plugin(plugin_id: str, enabled: bool = Query(True)):
    return await plugin_system.toggle(plugin_id, enabled)


@router.post("/plugins/install")
async def install_plugin(name: str = Query(...), display_name: Optional[str] = None, plugin_type: str = "custom"):
    return await plugin_system.install(name, display_name, plugin_type)


# --- Templates ---

@router.get("/templates")
async def list_templates(template_type: Optional[str] = None):
    return {"templates": await template_manager.list_templates(template_type)}


# --- Scenarios ---

@router.post("/scenarios/create")
async def create_scenario(request: ScenarioCreateRequest):
    return await scenario_builder.create(
        name=request.name, description=request.description,
        is_public=request.is_public, tags=request.tags,
    )


@router.get("/scenarios")
async def list_scenarios(public: Optional[bool] = None):
    return {"scenarios": await scenario_builder.list_scenarios(public)}


# --- Modules ---

@router.get("/modules")
async def list_modules(category: Optional[str] = None):
    return {"modules": await marketplace.list_modules(category)}


# --- Developer Tools ---

@router.get("/tools")
async def get_tools(tool_type: Optional[str] = None):
    return {"tools": await sdk.get_tools(tool_type)}


@router.get("/tools/api-docs")
async def get_api_documentation():
    return {"documentation": await sdk.get_api_documentation()}


# --- Workspaces ---

@router.post("/workspaces/create")
async def create_workspace(request: WorkspaceCreateRequest):
    return await workspace_manager.create_workspace(
        name=request.name, description=request.description, tags=request.tags,
    )


@router.get("/workspaces")
async def list_workspaces():
    return {"workspaces": await workspace_manager.list_workspaces()}


@router.get("/workspaces/{workspace_id}")
async def get_workspace(workspace_id: str):
    ws = await workspace_manager.get_workspace(workspace_id)
    if not ws: raise HTTPException(404, "Workspace not found")
    return ws


# --- Data Export ---

@router.post("/export")
async def export_data(request: ExportRequest):
    return await data_exporter.export(
        name=request.name, dataset_type=request.dataset_type,
        format=request.format, simulation_id=request.simulation_id, data=request.data,
    )


@router.get("/export/datasets")
async def list_datasets(dataset_type: Optional[str] = None):
    return {"datasets": await data_exporter.list_datasets(dataset_type)}


# --- Collaboration ---

@router.post("/collaboration/join")
async def join_workspace(workspace_id: str = Query(...), user_id: str = Query(...), role: str = "viewer"):
    return await collaboration.join_workspace(workspace_id, user_id, role)


@router.get("/collaboration/{workspace_id}/members")
async def get_collaborators(workspace_id: str):
    return {"members": await collaboration.get_collaborators(workspace_id)}
