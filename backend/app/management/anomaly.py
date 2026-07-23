import json
import random
from datetime import datetime

from app.management.persistence import mgmt_db
from app.domain.models.management import AnomalyAlert


class AnomalyDetector:
    """Detects unusual behavior and generates alerts."""

    ANOMALY_TEMPLATES = [
        {"type": "economic_collapse", "severity": "critical", "title": "Economic Collapse Detected",
         "desc": "GDP has dropped by more than 50% in the last 100 years.", "system": "economy",
         "cause": "Multiple factors including resource depletion and trade disruption.",
         "action": "Restore from last stable economic snapshot and investigate root causes."},
        {"type": "population_explosion", "severity": "warning", "title": "Rapid Population Growth",
         "desc": "Population growth rate exceeds 500% of normal.", "system": "population",
         "cause": "Unchecked growth parameters or missing population caps.",
         "action": "Review population growth model and apply regulatory adjustments."},
        {"type": "infinite_resources", "severity": "critical", "title": "Infinite Resource Generation",
         "desc": "A resource node appears to be generating infinite output.", "system": "resources",
         "cause": "Broken resource consumption loop or regeneration bug.",
         "action": "Isolate the resource node and recalculate resource balance."},
        {"type": "simulation_loop", "severity": "critical", "title": "Broken Simulation Loop",
         "desc": "A simulation subsystem is stuck in an infinite loop.", "system": "simulation",
         "cause": "Logic error in agent decision-making or event processing.",
         "action": "Force-break the loop and restart the affected subsystem."},
        {"type": "timeline_inconsistency", "severity": "warning", "title": "Timeline Inconsistency",
         "desc": "Events detected out of expected chronological order.", "system": "temporal",
         "cause": "Race condition in event recording or timeline branching.",
         "action": "Verify temporal integrity and reindex event sequence."},
        {"type": "agent_behavior", "severity": "warning", "title": "Unexpected Agent Behavior",
         "desc": "Multiple agents exhibiting identical decision patterns.", "system": "agents",
         "cause": "Possible AI reasoning cache poisoning or model collapse.",
         "action": "Clear agent reasoning cache and restart individual agent reasoning."},
        {"type": "data_corruption", "severity": "critical", "title": "Data Corruption Detected",
         "desc": "Invalid data detected in civilization records.", "system": "database",
         "cause": "Storage error or incomplete transaction.",
         "action": "Restore from latest valid snapshot and verify data integrity."},
        {"type": "performance_degradation", "severity": "warning", "title": "Performance Degradation",
         "desc": "Simulation tick time has exceeded acceptable thresholds.", "system": "performance",
         "cause": "High agent count, unoptimized queries, or memory pressure.",
         "action": "Apply performance optimizations and consider scaling resources."},
    ]

    async def scan(self) -> list[dict]:
        alerts = []
        for template in self.ANOMALY_TEMPLATES:
            if random.random() < 0.15:
                alert = AnomalyAlert(
                    alert_type=template["type"], severity=template["severity"],
                    title=template["title"], description=template["desc"],
                    affected_system=template["system"], cause=template["cause"],
                    suggested_action=template["action"],
                )
                saved = await mgmt_db.create_alert(alert)
                alerts.append({"id": saved.id, "type": saved.alert_type, "severity": saved.severity, "title": saved.title})
        return alerts

    async def get_alerts(self, resolved: bool = None, severity: str = None) -> list[dict]:
        alerts = await mgmt_db.get_alerts(
            resolved=(0 if resolved is False else 1 if resolved is True else None),
            severity=severity,
        )
        return [{
            "id": a.id, "type": a.alert_type, "severity": a.severity, "title": a.title,
            "description": a.description, "affected_system": a.affected_system,
            "cause": a.cause, "suggested_action": a.suggested_action,
            "resolved": bool(a.resolved), "detected_at": a.detected_at.isoformat() if a.detected_at else None,
        } for a in alerts]

    async def resolve_alert(self, alert_id: str) -> dict:
        a = await mgmt_db.resolve_alert(alert_id)
        if not a:
            return {"error": "Alert not found"}
        return {"id": a.id, "resolved": True, "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None}


anomaly_detector = AnomalyDetector()
