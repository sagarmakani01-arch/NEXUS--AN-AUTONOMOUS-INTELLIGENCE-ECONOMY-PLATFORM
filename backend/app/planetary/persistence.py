import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.planetary import (
    Planet, PlanetRegion, ClimateRecord, NaturalResource,
    EnvironmentalImpact, PlanetInfrastructure, Settlement,
    EnvironmentalEvent, SustainabilityMetrics,
)

logger = logging.getLogger("nexus.planetary.persistence")


async def create_planet(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = Planet(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def get_planet(planet_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(Planet).where(Planet.id == planet_id))
        o = r.scalar_one_or_none()
        return _planet_to_dict(o) if o else None


async def list_planets(status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Planet).where(Planet.status == status)
        stmt = stmt.order_by(Planet.created_at.desc())
        r = await session.execute(stmt)
        return [_planet_to_dict(p) for p in r.scalars().all()]


async def update_planet(planet_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(Planet).where(Planet.id == planet_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_region(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = PlanetRegion(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_regions(planet_id: str, terrain_type: str | None = None,
                       climate_zone: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(PlanetRegion).where(PlanetRegion.planet_id == planet_id)
        if terrain_type:
            stmt = stmt.where(PlanetRegion.terrain_type == terrain_type)
        if climate_zone:
            stmt = stmt.where(PlanetRegion.climate_zone == climate_zone)
        stmt = stmt.order_by(PlanetRegion.name)
        r = await session.execute(stmt)
        return [_region_to_dict(reg) for reg in r.scalars().all()]


async def get_region(region_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(PlanetRegion).where(PlanetRegion.id == region_id))
        o = r.scalar_one_or_none()
        return _region_to_dict(o) if o else None


async def update_region(region_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(PlanetRegion).where(PlanetRegion.id == region_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_climate_record(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = ClimateRecord(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_climate_records(planet_id: str, region_id: str | None = None,
                                limit: int = 30) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(ClimateRecord).where(ClimateRecord.planet_id == planet_id)
        if region_id:
            stmt = stmt.where(ClimateRecord.region_id == region_id)
        stmt = stmt.order_by(ClimateRecord.recorded_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [_climate_to_dict(c) for c in r.scalars().all()]


async def create_resource(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = NaturalResource(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_resources(planet_id: str, region_id: str | None = None,
                         resource_type: str | None = None,
                         discovered: bool | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(NaturalResource).where(NaturalResource.planet_id == planet_id)
        if region_id:
            stmt = stmt.where(NaturalResource.region_id == region_id)
        if resource_type:
            stmt = stmt.where(NaturalResource.resource_type == resource_type)
        if discovered is not None:
            stmt = stmt.where(NaturalResource.discovered == discovered)
        stmt = stmt.order_by(NaturalResource.market_value.desc())
        r = await session.execute(stmt)
        return [_resource_to_dict(res) for res in r.scalars().all()]


async def update_resource(resource_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(NaturalResource).where(NaturalResource.id == resource_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_impact(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = EnvironmentalImpact(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_impacts(planet_id: str, civilization_id: str | None = None,
                       limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(EnvironmentalImpact).where(EnvironmentalImpact.planet_id == planet_id)
        if civilization_id:
            stmt = stmt.where(EnvironmentalImpact.civilization_id == civilization_id)
        stmt = stmt.order_by(EnvironmentalImpact.recorded_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": i.id, "civilization_id": i.civilization_id,
             "impact_type": i.impact_type, "description": i.description,
             "severity": i.severity, "resource_depletion": i.resource_depletion,
             "land_use_change": i.land_use_change,
             "recorded_at": i.recorded_at.isoformat() if i.recorded_at else None}
            for i in r.scalars().all()
        ]


async def create_infrastructure(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = PlanetInfrastructure(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_infrastructure(planet_id: str, region_id: str | None = None,
                               civilization_id: str | None = None,
                               infra_type: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(PlanetInfrastructure).where(PlanetInfrastructure.planet_id == planet_id)
        if region_id:
            stmt = stmt.where(PlanetInfrastructure.region_id == region_id)
        if civilization_id:
            stmt = stmt.where(PlanetInfrastructure.civilization_id == civilization_id)
        if infra_type:
            stmt = stmt.where(PlanetInfrastructure.infra_type == infra_type)
        stmt = stmt.order_by(PlanetInfrastructure.level.desc())
        r = await session.execute(stmt)
        return [_infra_to_dict(i) for i in r.scalars().all()]


async def update_infrastructure(infra_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(PlanetInfrastructure).where(PlanetInfrastructure.id == infra_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_settlement(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = Settlement(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_settlements(planet_id: str, civilization_id: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Settlement).where(Settlement.planet_id == planet_id)
        if civilization_id:
            stmt = stmt.where(Settlement.civilization_id == civilization_id)
        stmt = stmt.order_by(Settlement.population.desc())
        r = await session.execute(stmt)
        return [_settlement_to_dict(s) for s in r.scalars().all()]


async def get_settlement(settlement_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(Settlement).where(Settlement.id == settlement_id))
        o = r.scalar_one_or_none()
        return _settlement_to_dict(o) if o else None


async def update_settlement(settlement_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(Settlement).where(Settlement.id == settlement_id))
        o = r.scalar_one_or_none()
        if o:
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            o.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_env_event(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = EnvironmentalEvent(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_env_events(planet_id: str, event_type: str | None = None,
                          status: str | None = None, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(EnvironmentalEvent).where(EnvironmentalEvent.planet_id == planet_id)
        if event_type:
            stmt = stmt.where(EnvironmentalEvent.event_type == event_type)
        if status:
            stmt = stmt.where(EnvironmentalEvent.status == status)
        stmt = stmt.order_by(EnvironmentalEvent.triggered_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [_env_event_to_dict(e) for e in r.scalars().all()]


async def create_sustainability(**kwargs) -> str:
    async with async_session_factory() as session:
        obj = SustainabilityMetrics(**kwargs)
        session.add(obj)
        await session.commit()
        return obj.id


async def list_sustainability(planet_id: str, civilization_id: str | None = None,
                               limit: int = 30) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(SustainabilityMetrics).where(SustainabilityMetrics.planet_id == planet_id)
        if civilization_id:
            stmt = stmt.where(SustainabilityMetrics.civilization_id == civilization_id)
        stmt = stmt.order_by(SustainabilityMetrics.recorded_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": s.id, "civilization_id": s.civilization_id,
             "resource_consumption_rate": s.resource_consumption_rate,
             "renewable_usage_pct": s.renewable_usage_pct,
             "infrastructure_efficiency": s.infrastructure_efficiency,
             "environmental_health": s.environmental_health,
             "carbon_footprint": s.carbon_footprint,
             "restoration_effort": s.restoration_effort,
             "sustainability_score": s.sustainability_score,
             "recorded_at": s.recorded_at.isoformat() if s.recorded_at else None}
            for s in r.scalars().all()
        ]


async def get_planet_stats() -> dict:
    async with async_session_factory() as session:
        planets = await session.execute(select(func.count(Planet.id)))
        regions = await session.execute(select(func.count(PlanetRegion.id)))
        resources = await session.execute(select(func.count(NaturalResource.id)))
        settlements = await session.execute(select(func.count(Settlement.id)))
        infra = await session.execute(select(func.count(PlanetInfrastructure.id)))
        events = await session.execute(select(func.count(EnvironmentalEvent.id)))
        return {
            "planets": planets.scalar() or 0,
            "regions": regions.scalar() or 0,
            "resources": resources.scalar() or 0,
            "settlements": settlements.scalar() or 0,
            "infrastructure": infra.scalar() or 0,
            "environmental_events": events.scalar() or 0,
        }


def _planet_to_dict(o) -> dict:
    return {
        "id": o.id, "name": o.name, "radius": o.radius,
        "seed": o.seed, "region_count": o.region_count,
        "total_population": o.total_population,
        "average_temperature": o.average_temperature,
        "average_rainfall": o.average_rainfall,
        "resource_richness": o.resource_richness,
        "environmental_health": o.environmental_health,
        "age_years": o.age_years, "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _region_to_dict(o) -> dict:
    return {
        "id": o.id, "planet_id": o.planet_id, "name": o.name,
        "terrain_type": o.terrain_type, "climate_zone": o.climate_zone,
        "pos_x": o.pos_x, "pos_y": o.pos_y, "area": o.area,
        "elevation": o.elevation, "water_nearby": o.water_nearby,
        "fertile": o.fertile, "habitability": o.habitability,
        "population": o.population, "developed": o.developed,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _climate_to_dict(o) -> dict:
    return {
        "id": o.id, "planet_id": o.planet_id, "region_id": o.region_id,
        "temperature": o.temperature, "rainfall": o.rainfall,
        "seasonality": o.seasonality, "drought_risk": o.drought_risk,
        "storm_risk": o.storm_risk,
        "growing_season_days": o.growing_season_days,
        "climate_type": o.climate_type,
        "recorded_at": o.recorded_at.isoformat() if o.recorded_at else None,
    }


def _resource_to_dict(o) -> dict:
    return {
        "id": o.id, "planet_id": o.planet_id, "region_id": o.region_id,
        "resource_type": o.resource_type, "name": o.name,
        "quantity": o.quantity, "max_quantity": o.max_quantity,
        "extraction_rate": o.extraction_rate,
        "regeneration_rate": o.regeneration_rate,
        "market_value": o.market_value, "renewable": o.renewable,
        "quality": o.quality, "discovered": o.discovered,
        "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _infra_to_dict(o) -> dict:
    return {
        "id": o.id, "planet_id": o.planet_id, "region_id": o.region_id,
        "civilization_id": o.civilization_id, "infra_type": o.infra_type,
        "name": o.name, "level": o.level, "efficiency": o.efficiency,
        "condition": o.condition, "capacity": o.capacity,
        "cost": o.cost, "status": o.status,
        "built_at": o.built_at.isoformat() if o.built_at else None,
    }


def _settlement_to_dict(o) -> dict:
    return {
        "id": o.id, "planet_id": o.planet_id, "region_id": o.region_id,
        "civilization_id": o.civilization_id, "name": o.name,
        "population": o.population, "economic_output": o.economic_output,
        "infrastructure_level": o.infrastructure_level,
        "research_capacity": o.research_capacity,
        "quality_of_life": o.quality_of_life,
        "education_level": o.education_level,
        "expansion_rate": o.expansion_rate,
        "status": o.status,
        "founded_at": o.founded_at.isoformat() if o.founded_at else None,
    }


def _env_event_to_dict(o) -> dict:
    return {
        "id": o.id, "planet_id": o.planet_id,
        "event_type": o.event_type, "region_id": o.region_id,
        "title": o.title, "description": o.description,
        "severity": o.severity, "duration_days": o.duration_days,
        "affected_population": o.affected_population,
        "resource_damage": o.resource_damage,
        "infrastructure_damage": o.infrastructure_damage,
        "status": o.status,
        "triggered_at": o.triggered_at.isoformat() if o.triggered_at else None,
        "resolved_at": o.resolved_at.isoformat() if o.resolved_at else None,
    }
