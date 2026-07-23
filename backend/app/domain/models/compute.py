import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class ComputeNode(Base):
    __tablename__ = "compute_nodes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    node_type = Column(String(50), default="worker")
    status = Column(String(50), default="offline")
    host = Column(String(255), nullable=True)
    port = Column(Integer, default=0)
    cpu_cores = Column(Integer, default=1)
    cpu_usage = Column(Float, default=0.0)
    gpu_count = Column(Integer, default=0)
    gpu_usage = Column(Float, default=0.0)
    memory_total_mb = Column(Float, default=1024)
    memory_used_mb = Column(Float, default=0.0)
    network_latency_ms = Column(Float, default=0.0)
    active_tasks = Column(Integer, default=0)
    max_tasks = Column(Integer, default=10)
    uptime_seconds = Column(Float, default=0.0)
    last_heartbeat = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ComputeNodeCapability(Base):
    __tablename__ = "compute_node_capabilities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(36), nullable=False)
    capability_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    performance_score = Column(Float, default=0.5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UniversePartition(Base):
    __tablename__ = "universe_partitions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(36), nullable=True)
    partition_key = Column(String(255), nullable=False)
    partition_type = Column(String(50), default="planet")
    universe_id = Column(String(36), nullable=True)
    parent_partition_id = Column(String(36), nullable=True)
    status = Column(String(50), default="unassigned")
    agent_count = Column(Integer, default=0)
    workload_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ComputeTask(Base):
    __tablename__ = "compute_tasks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(36), nullable=True)
    task_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(50), default="medium")
    status = Column(String(50), default="pending")
    source = Column(String(255), nullable=True)
    payload = Column(Text, default="{}")
    result = Column(Text, nullable=True)
    progress = Column(Float, default=0.0)
    estimated_cost = Column(Float, default=0.0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgentTaskPriority(Base):
    __tablename__ = "agent_task_priorities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), nullable=False)
    priority = Column(String(50), default="medium")
    reason = Column(String(255), nullable=True)
    assigned_node_id = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SyncState(Base):
    __tablename__ = "sync_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_node_id = Column(String(36), nullable=False)
    target_node_id = Column(String(36), nullable=False)
    sync_type = Column(String(100), default="state")
    status = Column(String(50), default="pending")
    data_size_bytes = Column(Integer, default=0)
    duration_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class WorkloadSnapshot(Base):
    __tablename__ = "workload_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(36), nullable=False)
    cpu_usage = Column(Float, default=0.0)
    memory_usage = Column(Float, default=0.0)
    active_tasks = Column(Integer, default=0)
    queue_depth = Column(Integer, default=0)
    avg_tick_time_ms = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class FaultEvent(Base):
    __tablename__ = "fault_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(36), nullable=True)
    fault_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="warning")
    description = Column(Text, nullable=True)
    affected_partitions = Column(Text, default="[]")
    recovery_action = Column(String(255), nullable=True)
    recovered = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    recovered_at = Column(DateTime(timezone=True), nullable=True)


class ComputeNodeStorage(Base):
    __tablename__ = "compute_node_storage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    node_id = Column(String(36), nullable=False)
    storage_type = Column(String(50), default="local")
    total_bytes = Column(Integer, default=0)
    used_bytes = Column(Integer, default=0)
    data_type = Column(String(100), default="simulation")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class DistributedClock(Base):
    __tablename__ = "distributed_clocks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clock_name = Column(String(255), nullable=False)
    tick_count = Column(Integer, default=0)
    time_scale = Column(Float, default=1.0)
    paused = Column(Integer, default=0)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
