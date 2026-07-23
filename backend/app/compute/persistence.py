import json
import time
from typing import Optional

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.compute import (
    ComputeNode, ComputeNodeCapability, UniversePartition, ComputeTask,
    AgentTaskPriority, SyncState, WorkloadSnapshot, FaultEvent,
    ComputeNodeStorage, DistributedClock,
)


class ComputeDB:
    # ── Nodes ──

    @staticmethod
    async def register_node(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = ComputeNode(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _node_to_dict(obj)

    @staticmethod
    async def get_node(node_id: str) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(ComputeNode).where(ComputeNode.id == node_id))
            o = r.scalar_one_or_none()
            return _node_to_dict(o) if o else None

    @staticmethod
    async def update_node(node_id: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(ComputeNode).where(ComputeNode.id == node_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = func.now()
            await s.commit()
            await s.refresh(o)
            return _node_to_dict(o)

    @staticmethod
    async def remove_node(node_id: str) -> bool:
        async with async_session_factory() as s:
            r = await s.execute(select(ComputeNode).where(ComputeNode.id == node_id))
            o = r.scalar_one_or_none()
            if not o:
                return False
            await s.delete(o)
            await s.commit()
            return True

    @staticmethod
    async def list_nodes(status: str = None) -> list[dict]:
        async with async_session_factory() as s:
            stmt = select(ComputeNode)
            if status:
                stmt = stmt.where(ComputeNode.status == status)
            stmt = stmt.order_by(ComputeNode.created_at.desc())
            r = await s.execute(stmt)
            return [_node_to_dict(o) for o in r.scalars().all()]

    @staticmethod
    async def get_available_node() -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(ComputeNode).where(
                    ComputeNode.status == "online",
                    ComputeNode.active_tasks < ComputeNode.max_tasks,
                ).order_by(ComputeNode.active_tasks.asc()).limit(1))
            o = r.scalar_one_or_none()
            return _node_to_dict(o) if o else None

    @staticmethod
    async def get_node_stats() -> dict:
        async with async_session_factory() as s:
            total = await s.execute(select(func.count(ComputeNode.id)))
            online = await s.execute(
                select(func.count(ComputeNode.id)).where(ComputeNode.status == "online"))
            total_tasks = await s.execute(select(func.sum(ComputeNode.active_tasks)))
            return {
                "total_nodes": total.scalar() or 0,
                "online_nodes": online.scalar() or 0,
                "total_active_tasks": total_tasks.scalar() or 0,
            }

    # ── Capabilities ──

    @staticmethod
    async def add_capability(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = ComputeNodeCapability(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _capability_to_dict(obj)

    @staticmethod
    async def get_capabilities(node_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(ComputeNodeCapability).where(ComputeNodeCapability.node_id == node_id))
            return [_capability_to_dict(o) for o in r.scalars().all()]

    # ── Partitions ──

    @staticmethod
    async def create_partition(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = UniversePartition(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _partition_to_dict(obj)

    @staticmethod
    async def update_partition(partition_id: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(UniversePartition).where(UniversePartition.id == partition_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _partition_to_dict(o)

    @staticmethod
    async def get_partitions(node_id: str = None) -> list[dict]:
        async with async_session_factory() as s:
            stmt = select(UniversePartition)
            if node_id:
                stmt = stmt.where(UniversePartition.node_id == node_id)
            stmt = stmt.order_by(UniversePartition.created_at.desc())
            r = await s.execute(stmt)
            return [_partition_to_dict(o) for o in r.scalars().all()]

    # ── Tasks ──

    @staticmethod
    async def create_task(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = ComputeTask(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _task_to_dict(obj)

    @staticmethod
    async def update_task(task_id: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(ComputeTask).where(ComputeTask.id == task_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _task_to_dict(o)

    @staticmethod
    async def get_tasks(node_id: str = None, status: str = None) -> list[dict]:
        async with async_session_factory() as s:
            stmt = select(ComputeTask)
            conds = []
            if node_id:
                conds.append(ComputeTask.node_id == node_id)
            if status:
                conds.append(ComputeTask.status == status)
            if conds:
                stmt = stmt.where(and_(*conds))
            stmt = stmt.order_by(ComputeTask.created_at.desc())
            r = await s.execute(stmt)
            return [_task_to_dict(o) for o in r.scalars().all()]

    # ── Agent Priorities ──

    @staticmethod
    async def set_agent_priority(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = AgentTaskPriority(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _priority_to_dict(obj)

    @staticmethod
    async def get_agent_priorities(node_id: str = None, priority: str = None) -> list[dict]:
        async with async_session_factory() as s:
            stmt = select(AgentTaskPriority)
            conds = []
            if node_id:
                conds.append(AgentTaskPriority.assigned_node_id == node_id)
            if priority:
                conds.append(AgentTaskPriority.priority == priority)
            if conds:
                stmt = stmt.where(and_(*conds))
            stmt = stmt.order_by(AgentTaskPriority.updated_at.desc())
            r = await s.execute(stmt)
            return [_priority_to_dict(o) for o in r.scalars().all()]

    # ── Sync States ──

    @staticmethod
    async def create_sync(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = SyncState(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _sync_to_dict(obj)

    @staticmethod
    async def get_sync_history(node_id: str = None, limit: int = 50) -> list[dict]:
        async with async_session_factory() as s:
            stmt = select(SyncState)
            if node_id:
                stmt = stmt.where(
                    (SyncState.source_node_id == node_id) | (SyncState.target_node_id == node_id))
            stmt = stmt.order_by(SyncState.created_at.desc()).limit(limit)
            r = await s.execute(stmt)
            return [_sync_to_dict(o) for o in r.scalars().all()]

    # ── Workload Snapshots ──

    @staticmethod
    async def record_workload(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = WorkloadSnapshot(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _workload_to_dict(obj)

    @staticmethod
    async def get_workload_history(node_id: str, limit: int = 20) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(WorkloadSnapshot).where(WorkloadSnapshot.node_id == node_id)
                .order_by(WorkloadSnapshot.recorded_at.desc()).limit(limit))
            return [_workload_to_dict(o) for o in r.scalars().all()]

    # ── Fault Events ──

    @staticmethod
    async def record_fault(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = FaultEvent(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _fault_to_dict(obj)

    @staticmethod
    async def update_fault_recovered(fault_id: str, recovered_at) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(FaultEvent).where(FaultEvent.id == fault_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            o.recovered = 1
            o.recovered_at = recovered_at
            await s.commit()
            await s.refresh(o)
            return _fault_to_dict(o)

    @staticmethod
    async def get_faults(node_id: str = None, limit: int = 50) -> list[dict]:
        async with async_session_factory() as s:
            stmt = select(FaultEvent)
            if node_id:
                stmt = stmt.where(FaultEvent.node_id == node_id)
            stmt = stmt.order_by(FaultEvent.created_at.desc()).limit(limit)
            r = await s.execute(stmt)
            return [_fault_to_dict(o) for o in r.scalars().all()]

    # ── Storage ──

    @staticmethod
    async def record_storage(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = ComputeNodeStorage(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _storage_to_dict(obj)

    @staticmethod
    async def get_storage(node_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(ComputeNodeStorage).where(ComputeNodeStorage.node_id == node_id))
            return [_storage_to_dict(o) for o in r.scalars().all()]

    # ── Distributed Clock ──

    @staticmethod
    async def get_or_create_clock(name: str = "nexus_universe") -> dict:
        async with async_session_factory() as s:
            r = await s.execute(select(DistributedClock).where(DistributedClock.clock_name == name))
            o = r.scalar_one_or_none()
            if o:
                return _clock_to_dict(o)
            obj = DistributedClock(clock_name=name)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _clock_to_dict(obj)

    @staticmethod
    async def update_clock(clock_name: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(DistributedClock).where(DistributedClock.clock_name == clock_name))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _clock_to_dict(o)


compute_db = ComputeDB()


def _node_to_dict(o: ComputeNode) -> dict:
    return {
        "id": o.id, "name": o.name, "node_type": o.node_type,
        "status": o.status, "host": o.host, "port": o.port,
        "cpu_cores": o.cpu_cores, "cpu_usage": o.cpu_usage,
        "gpu_count": o.gpu_count, "gpu_usage": o.gpu_usage,
        "memory_total_mb": o.memory_total_mb, "memory_used_mb": o.memory_used_mb,
        "network_latency_ms": o.network_latency_ms,
        "active_tasks": o.active_tasks, "max_tasks": o.max_tasks,
        "uptime_seconds": o.uptime_seconds,
        "last_heartbeat": o.last_heartbeat.isoformat() if o.last_heartbeat else None,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _capability_to_dict(o: ComputeNodeCapability) -> dict:
    return {
        "id": o.id, "node_id": o.node_id,
        "capability_type": o.capability_type, "description": o.description,
        "performance_score": o.performance_score,
    }


def _partition_to_dict(o: UniversePartition) -> dict:
    return {
        "id": o.id, "node_id": o.node_id,
        "partition_key": o.partition_key, "partition_type": o.partition_type,
        "universe_id": o.universe_id, "parent_partition_id": o.parent_partition_id,
        "status": o.status, "agent_count": o.agent_count,
        "workload_score": o.workload_score,
    }


def _task_to_dict(o: ComputeTask) -> dict:
    return {
        "id": o.id, "node_id": o.node_id, "task_type": o.task_type,
        "description": o.description, "priority": o.priority,
        "status": o.status, "source": o.source,
        "payload": json.loads(o.payload) if o.payload else {},
        "result": o.result, "progress": o.progress,
        "estimated_cost": o.estimated_cost,
        "started_at": o.started_at.isoformat() if o.started_at else None,
        "completed_at": o.completed_at.isoformat() if o.completed_at else None,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _priority_to_dict(o: AgentTaskPriority) -> dict:
    return {
        "id": o.id, "agent_id": o.agent_id, "priority": o.priority,
        "reason": o.reason, "assigned_node_id": o.assigned_node_id,
    }


def _sync_to_dict(o: SyncState) -> dict:
    return {
        "id": o.id, "source_node_id": o.source_node_id,
        "target_node_id": o.target_node_id, "sync_type": o.sync_type,
        "status": o.status, "data_size_bytes": o.data_size_bytes,
        "duration_ms": o.duration_ms,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _workload_to_dict(o: WorkloadSnapshot) -> dict:
    return {
        "id": o.id, "node_id": o.node_id,
        "cpu_usage": o.cpu_usage, "memory_usage": o.memory_usage,
        "active_tasks": o.active_tasks, "queue_depth": o.queue_depth,
        "avg_tick_time_ms": o.avg_tick_time_ms,
        "recorded_at": o.recorded_at.isoformat() if o.recorded_at else None,
    }


def _fault_to_dict(o: FaultEvent) -> dict:
    return {
        "id": o.id, "node_id": o.node_id, "fault_type": o.fault_type,
        "severity": o.severity, "description": o.description,
        "affected_partitions": json.loads(o.affected_partitions) if o.affected_partitions else [],
        "recovery_action": o.recovery_action, "recovered": bool(o.recovered),
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _storage_to_dict(o: ComputeNodeStorage) -> dict:
    return {
        "id": o.id, "node_id": o.node_id, "storage_type": o.storage_type,
        "total_bytes": o.total_bytes, "used_bytes": o.used_bytes,
        "data_type": o.data_type,
    }


def _clock_to_dict(o: DistributedClock) -> dict:
    return {
        "id": o.id, "clock_name": o.clock_name, "tick_count": o.tick_count,
        "time_scale": o.time_scale, "paused": bool(o.paused),
        "last_sync_at": o.last_sync_at.isoformat() if o.last_sync_at else None,
    }
