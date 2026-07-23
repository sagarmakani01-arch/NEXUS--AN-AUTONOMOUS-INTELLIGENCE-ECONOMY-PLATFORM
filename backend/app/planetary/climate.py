import logging
import random

logger = logging.getLogger("nexus.planetary.climate")


async def generate_climate(planet_id: str, regions: list[dict], seed: int = 42) -> list[dict]:
    from app.planetary import persistence as db
    records = []
    for region in regions:
        base_temp = {"tropical": 28, "subtropical": 22, "temperate": 15, "continental": 8, "polar": -5}
        temp = base_temp.get(region.get("climate_zone", "temperate"), 15)
        temp += random.uniform(-3, 3)
        rainfall = {"tropical": 2000, "subtropical": 1200, "temperate": 800, "continental": 500, "polar": 200}
        rain = rainfall.get(region.get("climate_zone", "temperate"), 800)
        rain += random.uniform(-200, 200)
        seasonality = 0.3 + random.uniform(0, 0.5)
        drought = 0.05 + random.uniform(0, 0.15)
        storm = 0.05 + random.uniform(0, 0.1)
        if region.get("terrain_type") == "coastline":
            storm += 0.1
        growing = int(120 + seasonality * 120)

        cid = await db.create_climate_record(
            planet_id=planet_id, region_id=region["id"],
            temperature=round(temp, 1), rainfall=round(rain, 1),
            seasonality=round(seasonality, 2), drought_risk=round(drought, 2),
            storm_risk=round(storm, 2), growing_season_days=growing,
            climate_type=region.get("climate_zone", "temperate"),
        )
        records.append({"id": cid, "region": region["name"], "temp": temp, "rain": rain})
    return records


async def evolve_climate(planet_id: str) -> dict:
    from app.planetary import persistence as db
    records = await db.list_climate_records(planet_id)
    if not records:
        return {}
    changed = 0
    for record in records[:5]:
        temp_delta = random.uniform(-0.3, 0.3)
        rain_delta = random.uniform(-10, 10)
        new_temp = record["temperature"] + temp_delta
        new_rain = record["rainfall"] + rain_delta
        await db.create_climate_record(
            planet_id=planet_id, region_id=record["region_id"],
            temperature=round(new_temp, 1), rainfall=round(max(0, new_rain), 1),
            seasonality=record["seasonality"],
            drought_risk=record["drought_risk"],
            storm_risk=record["storm_risk"],
            growing_season_days=record["growing_season_days"],
            climate_type=record["climate_type"],
        )
        changed += 1
    return {"records_updated": changed}


def get_state() -> dict:
    return {"initialized": True}
