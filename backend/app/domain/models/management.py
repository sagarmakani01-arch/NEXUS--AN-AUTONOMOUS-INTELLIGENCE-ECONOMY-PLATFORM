import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class UniverseHealthMetric(Base):
    __tablename__ = "universe_health_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(255), nullable=False)
    value = Column(Float, default=0.0)
    min_value = Column(Float, default=0.0)
    max_value = Column(Float, default=1.0)
    status = Column(String(50), default="healthy")
    details = Column(Text, default="{}")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class AnomalyAlert(Base):
    __tablename__ = "anomaly_alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="warning")
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    affected_system = Column(String(255), nullable=True)
    cause = Column(Text, nullable=True)
    suggested_action = Column(Text, nullable=True)
    resolved = Column(Integer, default=0)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class PerformanceSnapshot(Base):
    __tablename__ = "performance_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tick = Column(Integer, default=0)
    agent_count = Column(Integer, default=0)
    active_agents = Column(Integer, default=0)
    event_queue_size = Column(Integer, default=0)
    avg_tick_time_ms = Column(Float, default=0.0)
    memory_usage_mb = Column(Float, default=0.0)
    db_query_count = Column(Integer, default=0)
    cache_hit_rate = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ManagementLog(Base):
    __tablename__ = "management_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    log_type = Column(String(100), nullable=False)
    severity = Column(String(50), default="info")
    message = Column(Text, nullable=False)
    details = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OptimizationAction(Base):
    __tablename__ = "optimization_actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    action_type = Column(String(100), nullable=False)
    target = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    impact = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    applied_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class RecoveryOperation(Base):
    __tablename__ = "recovery_operations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_type = Column(String(100), nullable=False)
    target = Column(String(255), nullable=True)
    cause = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)
    success = Column(Integer, default=1)
    details = Column(Text, default="{}")
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
