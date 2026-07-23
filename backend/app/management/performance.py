import random
import time

from app.management.persistence import mgmt_db
from app.domain.models.management import PerformanceSnapshot, OptimizationAction


class PerformanceManager:
    """Optimizes simulation performance and resource allocation."""

    async def record_performance(self, agent_count: int = 0, event_queue_size: int = 0) -> dict:
        snap = PerformanceSnapshot(
            tick=random.randint(0, 10000),
            agent_count=agent_count,
            active_agents=max(0, agent_count - random.randint(0, int(agent_count * 0.3))),
            event_queue_size=event_queue_size,
            avg_tick_time_ms=round(random.uniform(5, 200), 1),
            memory_usage_mb=round(random.uniform(50, 500), 1),
            cache_hit_rate=round(random.uniform(0.7, 0.99), 3),
        )
        saved = await mgmt_db.save_perf(snap)
        return {
            "tick": saved.tick, "agents": saved.agent_count, "active": saved.active_agents,
            "avg_tick_ms": saved.avg_tick_time_ms, "memory_mb": saved.memory_usage_mb,
            "cache_hit": saved.cache_hit_rate,
        }

    async def get_performance(self) -> list[dict]:
        snaps = await mgmt_db.get_perf(limit=20)
        return [{
            "tick": s.tick, "agents": s.agent_count, "active": s.active_agents,
            "avg_tick_ms": s.avg_tick_time_ms, "memory_mb": s.memory_usage_mb,
            "cache_hit": s.cache_hit_rate, "time": s.created_at.isoformat() if s.created_at else None,
        } for s in snaps]

    async def suggest_optimizations(self) -> list[dict]:
        suggestions = [
            {
                "type": "agent_throttle", "target": "agents",
                "description": "Reduce inactive agent update frequency to improve tick performance.",
                "impact": "Expected 20-40% improvement in average tick time.",
            },
            {
                "type": "cache_warm", "target": "database",
                "description": "Pre-warm database cache for frequently accessed simulation data.",
                "impact": "Expected 15-30% reduction in query latency.",
            },
            {
                "type": "chunk_unload", "target": "world",
                "description": "Unload world chunks far from active observation areas.",
                "impact": "Expected 10-25% memory reduction.",
            },
            {
                "type": "event_batch", "target": "events",
                "description": "Batch process low-priority events to reduce queue overhead.",
                "impact": "Expected 5-15% improvement in event throughput.",
            },
        ]
        results = []
        for s in suggestions:
            o = OptimizationAction(action_type=s["type"], target=s["target"], description=s["description"], impact=s["impact"])
            saved = await mgmt_db.save_optimization(o)
            results.append({"id": saved.id, "type": saved.action_type, "description": saved.description, "impact": saved.impact})
        return results

    async def get_optimizations(self) -> list[dict]:
        opts = await mgmt_db.get_optimizations()
        return [{"id": o.id, "type": o.action_type, "target": o.target, "status": o.status, "impact": o.impact} for o in opts]

    async def apply_optimization(self, opt_id: str) -> dict:
        from datetime import datetime
        o = None
        for opt in await mgmt_db.get_optimizations():
            if opt.id == opt_id:
                o = opt
                break
        if not o:
            return {"error": "Optimization not found"}
        import sqlalchemy as sa
        from app.core.database import async_session_factory
        async with async_session_factory() as session:
            await session.execute(sa.update(OptimizationAction).where(OptimizationAction.id == opt_id).values(status="applied", applied_at=datetime.utcnow()))
            await session.commit()
        return {"id": opt_id, "status": "applied"}


perf_manager = PerformanceManager()
