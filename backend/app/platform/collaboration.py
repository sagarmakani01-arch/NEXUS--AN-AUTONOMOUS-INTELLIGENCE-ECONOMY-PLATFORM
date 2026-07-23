from datetime import datetime

from app.platform.persistence import platform_db
from app.domain.models.platform import CollaborationSession


class CollaborationManager:
    """Team collaboration for shared simulations and experiments."""

    async def join_workspace(self, workspace_id: str, user_id: str, role: str = "viewer") -> dict:
        session = CollaborationSession(workspace_id=workspace_id, user_id=user_id, role=role)
        saved = await platform_db.join_session(session)
        return {"id": saved.id, "workspace_id": workspace_id, "user_id": user_id, "role": role}

    async def get_collaborators(self, workspace_id: str) -> list[dict]:
        sessions = await platform_db.get_session_users(workspace_id)
        return [{"user_id": s.user_id, "role": s.role, "joined_at": s.joined_at.isoformat() if s.joined_at else None, "last_active_at": s.last_active_at.isoformat() if s.last_active_at else None} for s in sessions]

    async def share_scenario(self, scenario_id: str, user_id: str, permission: str = "view") -> dict:
        return {"scenario_id": scenario_id, "shared_with": user_id, "permission": permission, "shared_at": datetime.utcnow().isoformat()}


collaboration = CollaborationManager()
