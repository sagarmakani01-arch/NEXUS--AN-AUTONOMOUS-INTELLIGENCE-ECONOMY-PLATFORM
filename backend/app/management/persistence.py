import json
from typing import Optional
from datetime import datetime

from sqlalchemy import select, func
from app.core.database import async_session_factory as AsyncSessionLocal
from app.domain.models.management import (
    UniverseHealthMetric, AnomalyAlert, PerformanceSnapshot,
    ManagementLog, OptimizationAction, RecoveryOperation,
)


class ManagementPersistence:
    @staticmethod
    async def save_metric(m: UniverseHealthMetric) -> UniverseHealthMetric:
        async with AsyncSessionLocal() as s: s.add(m); await s.commit(); await s.refresh(m); return m

    @staticmethod
    async def get_metrics(limit: int = 50) -> list[UniverseHealthMetric]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(UniverseHealthMetric).order_by(UniverseHealthMetric.recorded_at.desc()).limit(limit))
            return list(r.scalars().all())

    @staticmethod
    async def create_alert(a: AnomalyAlert) -> AnomalyAlert:
        async with AsyncSessionLocal() as s: s.add(a); await s.commit(); await s.refresh(a); return a

    @staticmethod
    async def get_alerts(resolved: int = None, severity: str = None, limit: int = 50) -> list[AnomalyAlert]:
        async with AsyncSessionLocal() as s:
            q = select(AnomalyAlert)
            if resolved is not None: q = q.where(AnomalyAlert.resolved == resolved)
            if severity: q = q.where(AnomalyAlert.severity == severity)
            q = q.order_by(AnomalyAlert.detected_at.desc()).limit(limit)
            r = await s.execute(q); return list(r.scalars().all())

    @staticmethod
    async def resolve_alert(aid: str) -> Optional[AnomalyAlert]:
        async with AsyncSessionLocal() as s:
            a = await s.get(AnomalyAlert, aid)
            if not a: return None
            a.resolved = 1; a.resolved_at = datetime.utcnow()
            await s.commit(); await s.refresh(a); return a

    @staticmethod
    async def save_perf(p: PerformanceSnapshot) -> PerformanceSnapshot:
        async with AsyncSessionLocal() as s: s.add(p); await s.commit(); await s.refresh(p); return p

    @staticmethod
    async def get_perf(limit: int = 100) -> list[PerformanceSnapshot]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(PerformanceSnapshot).order_by(PerformanceSnapshot.created_at.desc()).limit(limit))
            return list(r.scalars().all())

    @staticmethod
    async def log(m: ManagementLog) -> ManagementLog:
        async with AsyncSessionLocal() as s: s.add(m); await s.commit(); await s.refresh(m); return m

    @staticmethod
    async def get_logs(log_type: str = None, severity: str = None, limit: int = 100) -> list[ManagementLog]:
        async with AsyncSessionLocal() as s:
            q = select(ManagementLog)
            if log_type: q = q.where(ManagementLog.log_type == log_type)
            if severity: q = q.where(ManagementLog.severity == severity)
            q = q.order_by(ManagementLog.created_at.desc()).limit(limit)
            r = await s.execute(q); return list(r.scalars().all())

    @staticmethod
    async def save_optimization(o: OptimizationAction) -> OptimizationAction:
        async with AsyncSessionLocal() as s: s.add(o); await s.commit(); await s.refresh(o); return o

    @staticmethod
    async def get_optimizations(status: str = None, limit: int = 50) -> list[OptimizationAction]:
        async with AsyncSessionLocal() as s:
            q = select(OptimizationAction)
            if status: q = q.where(OptimizationAction.status == status)
            q = q.order_by(OptimizationAction.created_at.desc()).limit(limit)
            r = await s.execute(q); return list(r.scalars().all())

    @staticmethod
    async def save_recovery(r: RecoveryOperation) -> RecoveryOperation:
        async with AsyncSessionLocal() as s: s.add(r); await s.commit(); await s.refresh(r); return r

    @staticmethod
    async def get_recoveries(limit: int = 50) -> list[RecoveryOperation]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(RecoveryOperation).order_by(RecoveryOperation.performed_at.desc()).limit(limit))
            return list(r.scalars().all())


mgmt_db = ManagementPersistence()
