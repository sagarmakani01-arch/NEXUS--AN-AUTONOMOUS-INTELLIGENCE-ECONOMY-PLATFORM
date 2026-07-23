import uuid

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.core.database import Base


class Planet(Base):
    __tablename__ = "planets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    radius = Column(Float, default=6371.0)
    seed = Column(Integer, default=42)
    region_count = Column(Integer, default=0)
    total_population = Column(Integer, default=0)
    average_temperature = Column(Float, default=15.0)
    average_rainfall = Column(Float, default=1000.0)
    resource_richness = Column(Float, default=50.0)
    environmental_health = Column(Float, default=80.0)
    age_years = Column(Float, default=0.0)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PlanetRegion(Base):
    __tablename__ = "planet_regions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    terrain_type = Column(String(50), nullable=False)
    climate_zone = Column(String(50), nullable=False)
    pos_x = Column(Float, default=0.0)
    pos_y = Column(Float, default=0.0)
    area = Column(Float, default=100.0)
    elevation = Column(Float, default=0.0)
    water_nearby = Column(Boolean, default=False)
    fertile = Column(Boolean, default=False)
    habitability = Column(Float, default=50.0)
    population = Column(Integer, default=0)
    developed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ClimateRecord(Base):
    __tablename__ = "climate_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    region_id = Column(String(36), nullable=True, index=True)
    temperature = Column(Float, default=15.0)
    rainfall = Column(Float, default=1000.0)
    seasonality = Column(Float, default=0.5)
    drought_risk = Column(Float, default=0.1)
    storm_risk = Column(Float, default=0.1)
    growing_season_days = Column(Integer, default=180)
    climate_type = Column(String(50), default="temperate")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class NaturalResource(Base):
    __tablename__ = "natural_resources"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    region_id = Column(String(36), nullable=True, index=True)
    resource_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=False)
    quantity = Column(Float, default=1000.0)
    max_quantity = Column(Float, default=1000.0)
    extraction_rate = Column(Float, default=0.0)
    regeneration_rate = Column(Float, default=0.0)
    market_value = Column(Float, default=10.0)
    renewable = Column(Boolean, default=False)
    quality = Column(Float, default=50.0)
    discovered = Column(Boolean, default=False)
    status = Column(String(50), default="available")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnvironmentalImpact(Base):
    __tablename__ = "environmental_impacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    civilization_id = Column(String(36), nullable=False, index=True)
    region_id = Column(String(36), nullable=True)
    impact_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Float, default=0.0)
    resource_depletion = Column(Float, default=0.0)
    land_use_change = Column(Float, default=0.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())


class PlanetInfrastructure(Base):
    __tablename__ = "planet_infrastructure"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    region_id = Column(String(36), nullable=False, index=True)
    civilization_id = Column(String(36), nullable=False, index=True)
    infra_type = Column(String(50), nullable=False)
    name = Column(String(255), nullable=True)
    level = Column(Integer, default=1)
    efficiency = Column(Float, default=50.0)
    condition = Column(Float, default=100.0)
    capacity = Column(Float, default=100.0)
    cost = Column(Float, default=0.0)
    status = Column(String(50), default="operational")
    built_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    region_id = Column(String(36), nullable=False, index=True)
    civilization_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    population = Column(Integer, default=100)
    economic_output = Column(Float, default=50.0)
    infrastructure_level = Column(Float, default=10.0)
    research_capacity = Column(Float, default=5.0)
    quality_of_life = Column(Float, default=50.0)
    education_level = Column(Float, default=10.0)
    expansion_rate = Column(Float, default=0.0)
    status = Column(String(50), default="growing")
    founded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class EnvironmentalEvent(Base):
    __tablename__ = "environmental_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    region_id = Column(String(36), nullable=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Float, default=0.0)
    duration_days = Column(Integer, default=1)
    affected_population = Column(Integer, default=0)
    resource_damage = Column(Float, default=0.0)
    infrastructure_damage = Column(Float, default=0.0)
    status = Column(String(50), default="active")
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class SustainabilityMetrics(Base):
    __tablename__ = "sustainability_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    planet_id = Column(String(36), nullable=False, index=True)
    civilization_id = Column(String(36), nullable=False, index=True)
    resource_consumption_rate = Column(Float, default=0.0)
    renewable_usage_pct = Column(Float, default=0.0)
    infrastructure_efficiency = Column(Float, default=50.0)
    environmental_health = Column(Float, default=80.0)
    carbon_footprint = Column(Float, default=0.0)
    restoration_effort = Column(Float, default=0.0)
    sustainability_score = Column(Float, default=50.0)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
