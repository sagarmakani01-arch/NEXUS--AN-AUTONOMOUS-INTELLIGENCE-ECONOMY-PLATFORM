import json
import uuid
from datetime import datetime

from app.platform.persistence import platform_db
from app.domain.models.platform import ExperimentWorkspace


class ExperimentWorkspaceManager:
    """Research environment for creating, cloning, and comparing experiments."""

    async def create_workspace(self, name: str, description: str = None, owner_id: str = None,
                                configuration: dict = None, tags: list = None) -> dict:
        ws = ExperimentWorkspace(
            name=name, description=description, owner_id=owner_id,
            configuration=json.dumps(configuration or {}), tags=json.dumps(tags or []),
        )
        saved = await platform_db.create_workspace(ws)
        return {"id": saved.id, "name": saved.name, "status": saved.status}

    async def list_workspaces(self, owner_id: str = None) -> list[dict]:
        workspaces = await platform_db.get_workspaces(owner_id)
        return [{
            "id": w.id, "name": w.name, "description": w.description, "owner_id": w.owner_id,
            "status": w.status, "tags": w.tags,
            "created_at": w.created_at.isoformat() if w.created_at else None,
        } for w in workspaces]

    async def get_workspace(self, workspace_id: str) -> Optional[dict]:
        workspaces = await platform_db.get_workspaces()
        ws = next((w for w in workspaces if w.id == workspace_id), None)
        if not ws: return None
        return {
            "id": ws.id, "name": ws.name, "description": ws.description,
            "status": ws.status, "configuration": ws.configuration, "tags": ws.tags,
            "created_at": ws.created_at.isoformat() if ws.created_at else None,
        }

    async def clone_civilization(self, workspace_id: str, source_sim_id: str, modifications: dict = None) -> dict:
        return {
            "workspace_id": workspace_id,
            "clone_id": str(uuid.uuid4()),
            "source_simulation": source_sim_id,
            "modifications": modifications or {},
            "message": "Civilization cloned. Ready for modified simulation run.",
        }

    async def export_findings(self, workspace_id: str, format: str = "json") -> dict:
        ws = await self.get_workspace(workspace_id)
        if not ws: return {"error": "Workspace not found"}
        return {
            "workspace_id": workspace_id,
            "name": ws["name"],
            "format": format,
            "exported_at": datetime.utcnow().isoformat(),
            "findings": {"observation_count": 0, "experiments_run": 0, "key_insights": []},
        }


workspace_manager = ExperimentWorkspaceManager()
