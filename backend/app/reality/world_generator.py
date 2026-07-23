import json
import random
import math

from app.reality.persistence import reality_db
from app.domain.models.virtual import VirtualWorldRegion, VirtualBuilding


class WorldGenerator:
    """Generates 3D world data from simulation state."""

    BUILDING_STYLES = {
        "modern": {"colors": ["#4a90d9", "#5a9fe6", "#3a80c9"], "height_range": (3, 8)},
        "industrial": {"colors": ["#8b7355", "#a0896b", "#6b5b45"], "height_range": (4, 12)},
        "research": {"colors": ["#e8e8e8", "#d0d0d0", "#ffffff"], "height_range": (2, 6)},
        "mediterranean": {"colors": ["#e8d5b7", "#f0e0c0", "#d4c4a0"], "height_range": (2, 5)},
        "futuristic": {"colors": ["#00d4aa", "#00b894", "#00a884"], "height_range": (5, 15)},
    }

    BUILDING_TYPES = {
        "house": (3, 4, 3), "apartment": (8, 10, 6), "factory": (15, 8, 20),
        "lab": (10, 5, 10), "office": (8, 12, 8), "university": (20, 8, 15),
        "government": (12, 15, 10), "market": (15, 4, 15), "park": (20, 0.5, 20),
        "road": (2, 0.2, 100),
    }

    TERRAIN_TYPES = ["plains", "hills", "mountains", "coastal", "desert", "forest", "tundra", "urban"]

    async def generate_region(self, region_x: int, region_z: int, biome: str = None, density: int = 30) -> dict:
        existing = await reality_db.get_region(region_x, region_z)
        if existing:
            return await self.get_region_data(region_x, region_z)

        biome = biome or random.choice(self.TERRAIN_TYPES)
        style = self._get_style_for_biome(biome)

        region = VirtualWorldRegion(
            region_x=region_x, region_z=region_z, label=f"Region ({region_x},{region_z})",
            biome=biome,
            terrain_data=json.dumps(self._generate_terrain(biome)),
        )
        region = await reality_db.save_region(region)

        buildings = []
        for _ in range(random.randint(density - 10, density)):
            bx = random.uniform(-45, 45)
            bz = random.uniform(-45, 45)
            btype = random.choice(list(self.BUILDING_TYPES.keys()))
            dims = self.BUILDING_TYPES[btype]
            bstyle = random.choice(style["colors"])

            building = VirtualBuilding(
                region_id=region.id,
                building_type=btype,
                label=f"{btype.title()}",
                pos_x=region_x * 100 + bx,
                pos_z=region_z * 100 + bz,
                width=dims[0] + random.uniform(-1, 1),
                height=dims[1] + random.uniform(-2, 2),
                depth=dims[2] + random.uniform(-1, 1),
                color=bstyle,
                style=random.choice(list(self.BUILDING_STYLES.keys())),
                occupants=random.randint(0, 50) if btype != "park" else 0,
                data=json.dumps({"generated": True, "population": random.randint(0, 100)}),
            )
            saved = await reality_db.save_building(building)
            buildings.append({"id": saved.id, "type": saved.building_type, "x": saved.pos_x, "z": saved.pos_z})
            region.building_count += 1

        await reality_db.save_region(region)

        return {"region_id": region.id, "x": region_x, "z": region_z, "biome": biome, "buildings": len(buildings)}

    async def get_region_data(self, region_x: int, region_z: int) -> Optional[dict]:
        region = await reality_db.get_region(region_x, region_z)
        if not region:
            return None
        buildings = await reality_db.get_buildings(region_id=region.id)
        entities = await reality_db.get_entities(region_id=region.id)
        return {
            "id": region.id, "x": region.region_x, "z": region.region_z,
            "biome": region.biome, "terrain": region.terrain_data,
            "buildings": [{
                "id": b.id, "type": b.building_type, "label": b.label,
                "x": b.pos_x, "y": b.pos_y, "z": b.pos_z,
                "w": b.width, "h": b.height, "d": b.depth,
                "color": b.color, "style": b.style, "occupants": b.occupants,
            } for b in buildings],
            "entities": [{
                "id": e.id, "name": e.name, "type": e.entity_type,
                "x": e.pos_x, "y": e.pos_y, "z": e.pos_z,
                "activity": e.activity, "speed": e.speed,
            } for e in entities],
        }

    def _generate_terrain(self, biome: str) -> dict:
        heights = []
        for _ in range(100):
            if biome == "mountains":
                h = random.uniform(-5, 15)
            elif biome == "hills":
                h = random.uniform(-2, 5)
            elif biome == "coastal":
                h = random.uniform(-3, 3)
            elif biome == "desert":
                h = random.uniform(-1, 2)
            else:
                h = random.uniform(-1, 4)
            heights.append(round(h, 1))
        return {"heights": heights, "biome": biome, "seed": random.randint(1, 10000)}

    def _get_style_for_biome(self, biome: str) -> dict:
        mapping = {
            "plains": self.BUILDING_STYLES["modern"],
            "urban": self.BUILDING_STYLES["futuristic"],
            "coastal": self.BUILDING_STYLES["mediterranean"],
            "desert": self.BUILDING_STYLES["industrial"],
            "forest": self.BUILDING_STYLES["modern"],
            "mountains": self.BUILDING_STYLES["industrial"],
            "hills": self.BUILDING_STYLES["mediterranean"],
            "tundra": self.BUILDING_STYLES["industrial"],
        }
        return mapping.get(biome, self.BUILDING_STYLES["modern"])

    async def get_nearby_regions(self, center_x: int, center_z: int, radius: int = 2) -> list[dict]:
        results = []
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                rx, rz = center_x + dx, center_z + dz
                region = await reality_db.get_region(rx, rz)
                if region:
                    bcount = region.building_count
                    ecount = region.entity_count
                else:
                    bcount = random.randint(5, 30) if abs(dx) + abs(dz) < 3 else 0
                    ecount = random.randint(0, 10)
                results.append({"x": rx, "z": rz, "buildings": bcount, "entities": ecount})
        return results


world_gen = WorldGenerator()
