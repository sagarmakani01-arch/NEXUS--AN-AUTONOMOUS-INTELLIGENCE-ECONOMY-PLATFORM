import logging
import random
import hashlib

logger = logging.getLogger("nexus.planetary.planet")

TERRAIN_TYPES = ["mountains", "plains", "forests", "deserts", "coastline", "lakes", "urban", "wetlands"]
CLIMATE_ZONES = ["tropical", "subtropical", "temperate", "continental", "polar"]
RESOURCE_TYPES = ["metals", "water", "energy", "construction_materials", "rare_minerals", "fertile_soil", "timber"]


def _seeded_random(seed: int, *args) -> float:
    h = hashlib.md5(f"{seed}-{args}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


async def generate_planet(name: str = "Nexus Prime", seed: int = 42,
                          region_count: int = 25) -> dict:
    from app.technology import persistence as tech_db
    planet_id = await tech_db.create_planet  # will use planetary persistence
    from app.planetary import persistence as db

    pid = await db.create_planet(
        name=name, seed=seed, region_count=0,
        average_temperature=15.0 + _seeded_random(seed, "temp") * 10 - 5,
        average_rainfall=800.0 + _seeded_random(seed, "rain") * 400,
        resource_richness=40.0 + _seeded_random(seed, "rich") * 40,
        environmental_health=85.0,
    )

    regions = []
    grid_size = int(region_count ** 0.5) + 1
    region_idx = 0
    for gx in range(grid_size):
        for gy in range(grid_size):
            if region_idx >= region_count:
                break
            terrain = TERRAIN_TYPES[int(_seeded_random(seed, gx, gy, "terrain") * len(TERRAIN_TYPES)) % len(TERRAIN_TYPES)]
            climate = CLIMATE_ZONES[int(_seeded_random(seed, gx, gy, "climate") * len(CLIMATE_ZONES)) % len(CLIMATE_ZONES)]
            elevation = _seeded_random(seed, gx, gy, "elev") * 3000
            water = terrain in ("coastline", "lakes", "wetlands") or _seeded_random(seed, gx, gy, "water") > 0.7
            fertile = terrain in ("plains", "forests", "wetlands") and climate in ("tropical", "subtropical", "temperate")
            habitability = 50.0
            if fertile:
                habitability += 20.0
            if water:
                habitability += 15.0
            if terrain in ("mountains", "deserts"):
                habitability -= 20.0
            habitability += _seeded_random(seed, gx, gy, "hab") * 10 - 5

            rid = await db.create_region(
                planet_id=pid, name=f"Region {gx}-{gy}",
                terrain_type=terrain, climate_zone=climate,
                pos_x=float(gx * 100), pos_y=float(gy * 100),
                area=100.0, elevation=round(elevation, 1),
                water_nearby=water, fertile=fertile,
                habitability=round(max(10.0, min(95.0, habitability)), 1),
            )
            regions.append({"id": rid, "name": f"Region {gx}-{gy}", "terrain": terrain})
            region_idx += 1

    await db.update_planet(pid, region_count=len(regions))

    resource_count = 0
    for region in regions:
        for rtype in RESOURCE_TYPES:
            if _seeded_random(seed, region["id"], rtype) > 0.6:
                qty = 500.0 + _seeded_random(seed, region["id"], rtype, "qty") * 2000
                renewable = rtype in ("water", "fertile_soil", "timber", "energy")
                await db.create_resource(
                    planet_id=pid, region_id=region["id"],
                    resource_type=rtype,
                    name=f"{rtype.replace('_', ' ').title()} of {region['name']}",
                    quantity=round(qty, 1),
                    max_quantity=round(qty, 1),
                    regeneration_rate=round(qty * 0.02, 2) if renewable else 0.0,
                    market_value=round(5.0 + _seeded_random(seed, region["id"], rtype, "val") * 30, 1),
                    renewable=renewable,
                    quality=round(40.0 + _seeded_random(seed, region["id"], rtype, "qual") * 50, 1),
                    discovered=True,
                )
                resource_count += 1

    logger.info("Planet '%s' generated: %d regions, %d resources", name, len(regions), resource_count)
    return await db.get_planet(pid)


async def get_terrain_influence(terrain_type: str) -> dict:
    influences = {
        "mountains": {"travel": 0.3, "construction": 0.4, "agriculture": 0.2, "settlement": 0.3},
        "plains": {"travel": 0.8, "construction": 0.7, "agriculture": 0.9, "settlement": 0.8},
        "forests": {"travel": 0.5, "construction": 0.5, "agriculture": 0.6, "settlement": 0.5},
        "deserts": {"travel": 0.4, "construction": 0.3, "agriculture": 0.1, "settlement": 0.2},
        "coastline": {"travel": 0.6, "construction": 0.6, "agriculture": 0.5, "settlement": 0.7},
        "lakes": {"travel": 0.4, "construction": 0.5, "agriculture": 0.6, "settlement": 0.6},
        "urban": {"travel": 0.9, "construction": 0.9, "agriculture": 0.1, "settlement": 0.9},
        "wetlands": {"travel": 0.3, "construction": 0.3, "agriculture": 0.5, "settlement": 0.3},
    }
    return influences.get(terrain_type, {"travel": 0.5, "construction": 0.5, "agriculture": 0.5, "settlement": 0.5})


def get_state() -> dict:
    return {"terrain_types": TERRAIN_TYPES, "climate_zones": CLIMATE_ZONES, "resource_types": RESOURCE_TYPES}
