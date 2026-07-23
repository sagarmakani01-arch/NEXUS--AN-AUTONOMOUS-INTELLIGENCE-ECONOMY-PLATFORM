import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class TemporalClock(Base):
    __tablename__ = "temporal_clocks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    tick_count = Column(Integer, default=0)
    current_year = Column(Integer, default=2025)
    current_day = Column(Integer, default=1)
    current_hour = Column(Integer, default=0)
    time_scale = Column(Float, default=1.0)
    paused = Column(Boolean, default=False)
    status = Column(String(50), default="running")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class HistoricalEvent(Base):
    __tablename__ = "historical_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clock_id = Column(String(36), nullable=False, index=True)
    timeline_id = Column(String(36), nullable=True, index=True)
    event_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(255), nullable=True)
    participants = Column(Text, default="[]")
    cause = Column(Text, nullable=True)
    outcome = Column(Text, nullable=True)
    impact_score = Column(Float, default=0.0)
    tick_occurred = Column(Integer, nullable=False)
    year_occurred = Column(Integer, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class WorldSnapshot(Base):
    __tablename__ = "world_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clock_id = Column(String(36), nullable=False, index=True)
    timeline_id = Column(String(36), nullable=True, index=True)
    label = Column(String(255), nullable=True)
    tick = Column(Integer, nullable=False)
    year = Column(Integer, nullable=True)
    population_state = Column(Text, default="{}")
    economy_state = Column(Text, default="{}")
    technology_state = Column(Text, default="{}")
    government_state = Column(Text, default="{}")
    resources_state = Column(Text, default="{}")
    environment_state = Column(Text, default="{}")
    full_state = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Timeline(Base):
    __tablename__ = "timelines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    parent_timeline_id = Column(String(36), nullable=True)
    branch_point_tick = Column(Integer, nullable=True)
    branch_point_year = Column(Integer, nullable=True)
    divergence_cause = Column(Text, nullable=True)
    event_count = Column(Integer, default=0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CausalEdge(Base):
    __tablename__ = "causal_edges"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_event_id = Column(String(36), nullable=False, index=True)
    target_event_id = Column(String(36), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)
    strength = Column(Float, default=0.5)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HistoricalAnalytics(Base):
    __tablename__ = "historical_analytics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timeline_id = Column(String(36), nullable=True, index=True)
    analytics_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    data = Column(Text, default="{}")
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
