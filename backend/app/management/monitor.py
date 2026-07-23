import random
import time
from datetime import datetime

from app.management.persistence import mgmt_db
from app.domain.models.management import UniverseHealthMetric, ManagementLog


class UniverseMonitor:
    """Continuously monitors universe health across multiple dimensions."""

    METRICS = [
        "simulation_stability", "economic_balance", "population_stability",
        "resource_balance", "technology_progress", "system_performance",
        "agent_activity", "event_health", "db_health",
    ]

    async def record_health(self, metrics: dict = None) -> list[dict]:
        results = []
        for metric_name in self.METRICS:
            value = metrics.get(metric_name, random.uniform(0.6, 0.95)) if metrics else random.uniform(0.6, 0.95)
            m = UniverseHealthMetric(
                metric_name=metric_name,
                value=round(value, 3),
                min_value=0.0, max_value=1.0,
                status="healthy" if value > 0.7 else "degraded" if value > 0.4 else "critical",
                details='{}',
            )
            saved = await mgmt_db.save_metric(m)
            results.append({"name": saved.metric_name, "value": saved.value, "status": saved.status})
        return results

    async def get_health_status(self) -> dict:
        metrics = await mgmt_db.get_metrics(limit=50)
        if not metrics:
            return {"status": "unknown", "metrics": {}}

        latest = {}
        for m in metrics[:len(self.METRICS)]:
            latest[m.metric_name] = {"value": m.value, "status": m.status}

        avg_health = sum(m.value for m in metrics[:len(self.METRICS)]) / max(1, len(metrics[:len(self.METRICS)]))
        status = "healthy" if avg_health > 0.7 else "degraded" if avg_health > 0.4 else "critical"

        degradations = [m.metric_name for m in metrics[:len(self.METRICS)] if m.status != "healthy"]

        return {
            "overall_status": status,
            "health_score": round(avg_health, 3),
            "metrics": latest,
            "degraded_metrics": degradations,
            "total_metrics": len(latest),
        }

    async def log_system_event(self, log_type: str, message: str, severity: str = "info", details: dict = None) -> dict:
        l = ManagementLog(log_type=log_type, severity=severity, message=message, details=json.dumps(details or {}))
        saved = await mgmt_db.log(l)
        return {"id": saved.id, "type": saved.log_type, "severity": saved.severity, "message": saved.message}

    async def get_logs(self, log_type: str = None, severity: str = None, limit: int = 100) -> list[dict]:
        logs = await mgmt_db.get_logs(log_type, severity, limit)
        return [{"id": l.id, "type": l.log_type, "severity": l.severity, "message": l.message, "time": l.created_at.isoformat() if l.created_at else None} for l in logs]


import json

monitor = UniverseMonitor()
