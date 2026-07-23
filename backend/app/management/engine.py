import random

from app.management.monitor import monitor
from app.management.performance import perf_manager
from app.management.anomaly import anomaly_detector
from app.management.integrity import integrity
from app.management.logs import admin_logs


class ManagementEngine:
    """Orchestrates the universe management layer."""

    def __init__(self):
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        await admin_logs.log("system", "Universe Management Engine initialized", "info")
        self._initialized = True

    async def tick(self, agent_count: int = 0) -> dict:
        if not self._initialized:
            await self.initialize()

        health = await monitor.record_health()
        perf = await perf_manager.record_performance(agent_count=agent_count)
        anomalies = await anomaly_detector.scan()
        checks = await integrity.check_all()

        return {
            "health_metrics": len(health),
            "performance": perf,
            "anomalies_detected": len(anomalies),
            "integrity_checks": len(checks),
        }

    async def get_full_state(self) -> dict:
        return {
            "initialized": self._initialized,
            "health": await monitor.get_health_status(),
        }


mgmt_engine = ManagementEngine()
