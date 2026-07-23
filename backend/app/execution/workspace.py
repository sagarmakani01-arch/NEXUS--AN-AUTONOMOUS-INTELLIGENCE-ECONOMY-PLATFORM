from __future__ import annotations

import json
import logging

from app.execution import persistence as ep

logger = logging.getLogger("nexus.execution.workspace")


class WorkEnvironment:
    async def create_workspace(self, agent_id: str, project_id: str | None = None, name: str = "") -> dict:
        ws_name = name or f"Workspace-{agent_id[:8]}"
        ws = await ep.create_workspace(agent_id=agent_id, project_id=project_id, name=ws_name)
        logger.info("workspace_created agent=%s project=%s", agent_id, project_id)
        return ws

    async def get_workspace(self, workspace_id: str) -> dict | None:
        return await ep.get_workspace(workspace_id)

    async def add_file(self, workspace_id: str, filename: str, content: str, file_type: str = "document") -> dict:
        ws = await ep.get_workspace(workspace_id)
        if not ws:
            return {"error": "Workspace not found"}
        files = ws.get("files", [])
        files.append({
            "name": filename,
            "type": file_type,
            "size": len(content),
            "content_preview": content[:200] if content else "",
        })
        await ep.update_workspace(workspace_id, files_json=json.dumps(files))
        return {"filename": filename, "added": True, "total_files": len(files)}

    async def add_note(self, workspace_id: str, note: str) -> dict:
        ws = await ep.get_workspace(workspace_id)
        if not ws:
            return {"error": "Workspace not found"}
        existing = ws.get("notes", "")
        new_notes = f"{existing}\n---\n{note}" if existing else note
        await ep.update_workspace(workspace_id, notes=new_notes)
        return {"note_added": True, "total_notes": len(new_notes.split("\n"))}

    async def add_artifact(self, workspace_id: str, name: str, artifact_type: str, description: str = "") -> dict:
        ws = await ep.get_workspace(workspace_id)
        if not ws:
            return {"error": "Workspace not found"}
        artifacts = ws.get("artifacts", [])
        artifacts.append({
            "name": name,
            "type": artifact_type,
            "description": description,
        })
        await ep.update_workspace(workspace_id, artifacts_json=json.dumps(artifacts))
        return {"artifact_name": name, "added": True, "total_artifacts": len(artifacts)}

    async def record_task(self, workspace_id: str, task_id: str, status: str, result: str = "") -> dict:
        ws = await ep.get_workspace(workspace_id)
        if not ws:
            return {"error": "Workspace not found"}
        history = ws.get("task_history", [])
        history.append({
            "task_id": task_id,
            "status": status,
            "result": result[:200] if result else "",
        })
        await ep.update_workspace(workspace_id, task_history_json=json.dumps(history))
        return {"recorded": True, "total_history": len(history)}

    async def get_workspace_summary(self, workspace_id: str) -> dict:
        ws = await ep.get_workspace(workspace_id)
        if not ws:
            return {"error": "Workspace not found"}
        return {
            "id": ws["id"],
            "name": ws["name"],
            "project_id": ws.get("project_id"),
            "file_count": len(ws.get("files", [])),
            "note_count": len(ws.get("notes", "").split("\n")) if ws.get("notes") else 0,
            "artifact_count": len(ws.get("artifacts", [])),
            "task_history_count": len(ws.get("task_history", [])),
            "status": ws.get("status"),
        }

    async def list_agent_workspaces(self, agent_id: str) -> list[dict]:
        workspaces = await ep.list_workspaces(agent_id=agent_id)
        return [
            {
                "id": w["id"],
                "name": w["name"],
                "project_id": w.get("project_id"),
                "status": w["status"],
                "file_count": len(w.get("files", [])),
                "artifact_count": len(w.get("artifacts", [])),
            }
            for w in workspaces
        ]


work_environment = WorkEnvironment()
