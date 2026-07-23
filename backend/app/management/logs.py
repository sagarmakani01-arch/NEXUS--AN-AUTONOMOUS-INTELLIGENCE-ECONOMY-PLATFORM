from datetime import datetime
from app.management.persistence import mgmt_db
from app.domain.models.management import ManagementLog


class AdminLogManager:
    """Stores and retrieves universe management logs."""

    async def log(self, log_type: str, message: str, severity: str = "info", details: dict = None) -> dict:
        import json
        l = ManagementLog(log_type=log_type, severity=severity, message=message, details=json.dumps(details or {}))
        saved = await mgmt_db.log(l)
        return {"id": saved.id, "type": saved.log_type, "severity": saved.severity, "message": saved.message}

    async def query(self, log_type: str = None, severity: str = None, limit: int = 100) -> list[dict]:
        logs = await mgmt_db.get_logs(log_type, severity, limit)
        return [{
            "id": l.id, "type": l.log_type, "severity": l.severity,
            "message": l.message, "time": l.created_at.isoformat() if l.created_at else None,
        } for l in logs]


admin_logs = AdminLogManager()
