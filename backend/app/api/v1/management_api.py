from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.management.engine import mgmt_engine
from app.management.monitor import monitor
from app.management.anomaly import anomaly_detector
from app.management.performance import perf_manager
from app.management.integrity import integrity, recovery
from app.management.assistant import assistant
from app.management.control import control_panel
from app.management.logs import admin_logs

router = APIRouter(prefix="/api/v1/admin", tags=["Management"])


class AccelRequest(BaseModel):
    factor: float


# --- State ---

@router.get("/state")
async def get_admin_state():
    return await mgmt_engine.get_full_state()


# --- Health ---

@router.get("/health")
async def get_health():
    return await monitor.get_health_status()


@router.post("/health/record")
async def record_health():
    return {"metrics": await monitor.record_health()}


# --- Anomalies ---

@router.get("/anomalies")
async def list_anomalies(resolved: Optional[bool] = None, severity: Optional[str] = None):
    return {"anomalies": await anomaly_detector.get_alerts(resolved, severity)}


@router.post("/anomalies/{alert_id}/resolve")
async def resolve_anomaly(alert_id: str):
    return await anomaly_detector.resolve_alert(alert_id)


# --- Performance ---

@router.get("/performance")
async def get_performance():
    return {"snapshots": await perf_manager.get_performance()}


@router.get("/performance/optimizations")
async def get_optimizations():
    return {"optimizations": await perf_manager.get_optimizations()}


@router.post("/performance/optimizations")
async def suggest_optimizations():
    return {"optimizations": await perf_manager.suggest_optimizations()}


@router.post("/performance/optimizations/{opt_id}/apply")
async def apply_optimization(opt_id: str):
    return await perf_manager.apply_optimization(opt_id)


# --- Integrity ---

@router.get("/integrity")
async def check_integrity():
    return {"checks": await integrity.check_all()}


@router.post("/integrity/repair/{issue_type}")
async def repair_integrity(issue_type: str):
    return await integrity.repair(issue_type)


# --- Recovery ---

@router.post("/recovery/restore-snapshot")
async def restore_snapshot(snapshot_id: str = Query(...)):
    return await recovery.restore_snapshot(snapshot_id)


@router.post("/recovery/rollback-event")
async def rollback_event(event_id: str = Query(...)):
    return await recovery.rollback_event(event_id)


@router.post("/recovery/restart-module")
async def restart_module(module_name: str = Query(...)):
    return await recovery.restart_module(module_name)


@router.get("/recovery/history")
async def get_recovery_history():
    return {"recoveries": await recovery.get_history()}


# --- Logs ---

@router.get("/logs")
async def get_logs(log_type: Optional[str] = None, severity: Optional[str] = None, limit: int = 100):
    return {"logs": await admin_logs.query(log_type, severity, limit)}


# --- Control ---

@router.post("/control/pause")
async def pause_universe():
    return await control_panel.pause_all()


@router.post("/control/resume")
async def resume_universe():
    return await control_panel.resume_all()


@router.post("/control/accelerate")
async def accelerate_time(request: AccelRequest):
    return await control_panel.accelerate_time(request.factor)


@router.post("/control/snapshot")
async def create_snapshot():
    return await control_panel.create_snapshot()


@router.get("/control/status")
async def get_control_status():
    return await control_panel.get_control_status()


# --- Assistant ---

@router.get("/assistant/analyze")
async def analyze_simulation():
    return await assistant.analyze_simulation()


@router.get("/assistant/explain/{event_type}")
async def explain_event(event_type: str):
    return await assistant.explain_event(event_type)
