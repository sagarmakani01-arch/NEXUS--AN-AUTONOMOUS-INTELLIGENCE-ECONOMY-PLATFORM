import json
from typing import Optional

from sqlalchemy import select
from app.core.database import async_session_factory as AsyncSessionLocal
from app.domain.models.virtual import (
    VirtualWorldRegion, VirtualBuilding, VirtualEntity,
    VirtualCameraState, CinematicEvent, InteractionLog,
)


class RealityPersistence:
    @staticmethod
    async def save_region(r: VirtualWorldRegion) -> VirtualWorldRegion:
        async with AsyncSessionLocal() as s: s.add(r); await s.commit(); await s.refresh(r); return r

    @staticmethod
    async def get_region(rx: int, rz: int) -> Optional[VirtualWorldRegion]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(VirtualWorldRegion).where(VirtualWorldRegion.region_x == rx, VirtualWorldRegion.region_z == rz))
            return r.scalar_one_or_none()

    @staticmethod
    async def get_regions() -> list[VirtualWorldRegion]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(VirtualWorldRegion)); return list(r.scalars().all())

    @staticmethod
    async def save_building(b: VirtualBuilding) -> VirtualBuilding:
        async with AsyncSessionLocal() as s: s.add(b); await s.commit(); await s.refresh(b); return b

    @staticmethod
    async def get_buildings(region_id: str = None, btype: str = None) -> list[VirtualBuilding]:
        async with AsyncSessionLocal() as s:
            q = select(VirtualBuilding)
            if region_id: q = q.where(VirtualBuilding.region_id == region_id)
            if btype: q = q.where(VirtualBuilding.building_type == btype)
            r = await s.execute(q); return list(r.scalars().all())

    @staticmethod
    async def get_building(bid: str) -> Optional[VirtualBuilding]:
        async with AsyncSessionLocal() as s: return await s.get(VirtualBuilding, bid)

    @staticmethod
    async def save_entity(e: VirtualEntity) -> VirtualEntity:
        async with AsyncSessionLocal() as s: s.add(e); await s.commit(); await s.refresh(e); return e

    @staticmethod
    async def get_entities(region_id: str = None) -> list[VirtualEntity]:
        async with AsyncSessionLocal() as s:
            q = select(VirtualEntity)
            if region_id: q = q.where(VirtualEntity.region_id == region_id)
            r = await s.execute(q); return list(r.scalars().all())

    @staticmethod
    async def get_entity_by_agent(aid: str) -> Optional[VirtualEntity]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(VirtualEntity).where(VirtualEntity.simulation_agent_id == aid))
            return r.scalar_one_or_none()

    @staticmethod
    async def save_camera(c: VirtualCameraState) -> VirtualCameraState:
        async with AsyncSessionLocal() as s: s.add(c); await s.commit(); await s.refresh(c); return c

    @staticmethod
    async def get_cameras() -> list[VirtualCameraState]:
        async with AsyncSessionLocal() as s:
            r = await s.execute(select(VirtualCameraState)); return list(r.scalars().all())

    @staticmethod
    async def save_cinematic(c: CinematicEvent) -> CinematicEvent:
        async with AsyncSessionLocal() as s: s.add(c); await s.commit(); await s.refresh(c); return c

    @staticmethod
    async def get_cinematic_events(triggered: int = None, limit: int = 20) -> list[CinematicEvent]:
        async with AsyncSessionLocal() as s:
            q = select(CinematicEvent)
            if triggered is not None: q = q.where(CinematicEvent.triggered == triggered)
            q = q.order_by(CinematicEvent.priority.desc()).limit(limit)
            r = await s.execute(q); return list(r.scalars().all())

    @staticmethod
    async def log_interaction(l: InteractionLog) -> InteractionLog:
        async with AsyncSessionLocal() as s: s.add(l); await s.commit(); await s.refresh(l); return l

    @staticmethod
    async def get_interactions(user_id: str = None, limit: int = 50) -> list[InteractionLog]:
        async with AsyncSessionLocal() as s:
            q = select(InteractionLog)
            if user_id: q = q.where(InteractionLog.user_id == user_id)
            q = q.order_by(InteractionLog.created_at.desc()).limit(limit)
            r = await s.execute(q); return list(r.scalars().all())


reality_db = RealityPersistence()
