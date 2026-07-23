import uuid

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class VirtualWorldRegion(Base):
    __tablename__ = "virtual_regions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    region_x = Column(Integer, nullable=False)
    region_z = Column(Integer, nullable=False)
    label = Column(String(255), nullable=True)
    biome = Column(String(100), default="plains")
    terrain_data = Column(Text, default="{}")
    building_count = Column(Integer, default=0)
    entity_count = Column(Integer, default=0)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class VirtualBuilding(Base):
    __tablename__ = "virtual_buildings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    region_id = Column(String(36), nullable=True, index=True)
    simulation_ref_id = Column(String(36), nullable=True, index=True)
    building_type = Column(String(100), nullable=False)
    label = Column(String(255), nullable=True)
    pos_x = Column(Float, nullable=False)
    pos_y = Column(Float, default=0.0)
    pos_z = Column(Float, nullable=False)
    width = Column(Float, default=10.0)
    height = Column(Float, default=5.0)
    depth = Column(Float, default=10.0)
    color = Column(String(50), default="#4a90d9")
    style = Column(String(100), default="modern")
    occupants = Column(Integer, default=0)
    data = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class VirtualEntity(Base):
    __tablename__ = "virtual_entities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    region_id = Column(String(36), nullable=True, index=True)
    simulation_agent_id = Column(String(36), nullable=True, index=True)
    name = Column(String(255), nullable=True)
    entity_type = Column(String(100), default="citizen")
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    pos_z = Column(Float, default=0.0)
    target_x = Column(Float, default=0.0)
    target_y = Column(Float, default=0.0)
    target_z = Column(Float, default=0.0)
    speed = Column(Float, default=1.0)
    activity = Column(String(100), default="idle")
    avatar_data = Column(Text, default="{}")
    last_update = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class VirtualCameraState(Base):
    __tablename__ = "virtual_camera_states"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    cam_x = Column(Float, default=0.0)
    cam_y = Column(Float, default=50.0)
    cam_z = Column(Float, default=0.0)
    target_x = Column(Float, default=0.0)
    target_y = Column(Float, default=0.0)
    target_z = Column(Float, default=0.0)
    fov = Column(Float, default=60.0)
    mode = Column(String(50), default="free")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CinematicEvent(Base):
    __tablename__ = "cinematic_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    target_entity_id = Column(String(36), nullable=True)
    target_building_id = Column(String(36), nullable=True)
    cam_position = Column(Text, default="{}")
    cam_target = Column(Text, default="{}")
    duration_seconds = Column(Float, default=10.0)
    priority = Column(Float, default=0.5)
    triggered = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=True)
    interaction_type = Column(String(100), nullable=False)
    target_type = Column(String(100), nullable=True)
    target_id = Column(String(36), nullable=True)
    query = Column(Text, nullable=True)
    response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
