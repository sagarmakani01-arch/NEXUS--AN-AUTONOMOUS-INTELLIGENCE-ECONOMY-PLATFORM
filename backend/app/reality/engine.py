import random

from app.reality.world_generator import world_gen
from app.reality.entity_tracker import entity_tracker
from app.reality.cinematic_director import cinematic_director
from app.reality.interaction import interaction_handler
from app.reality.persistence import reality_db


class RealityEngine:
    """Orchestrates the 3D reality and exploration layer."""

    def __init__(self):
        self._initialized = False

    async def initialize(self):
        if self._initialized:
            return
        self._initialized = True

    async def tick(self) -> dict:
        if not self._initialized:
            await self.initialize()

        entities_moved = await entity_tracker.tick_movement()

        if random.random() < 0.02:
            await cinematic_director.generate_event()

        return {
            "entities_moved": entities_moved,
            "cinematic": await cinematic_director.get_state(),
        }

    async def explore_region(self, region_x: int, region_z: int) -> dict:
        region = await world_gen.get_region_data(region_x, region_z)
        if region:
            return region
        return await world_gen.generate_region(region_x, region_z)

    async def get_full_state(self) -> dict:
        regions = await reality_db.get_regions()
        entities = await reality_db.get_entities()
        buildings = []
        for r in regions:
            b = await reality_db.get_buildings(region_id=r.id)
            buildings.extend(b)
        return {
            "initialized": self._initialized,
            "regions": len(regions),
            "buildings": len(buildings),
            "entities": len(entities),
            "cinematic": await cinematic_director.get_state(),
        }


reality_engine = RealityEngine()
