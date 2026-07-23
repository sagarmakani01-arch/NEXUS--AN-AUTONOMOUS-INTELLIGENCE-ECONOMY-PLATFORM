import logging
import random

logger = logging.getLogger("nexus.planetary.resources")


async def extract_resource(resource_id: str, amount: float) -> dict | None:
    from app.planetary import persistence as db
    resources = await db.list_resources(planet_id="")
    resource = next((r for r in resources if r["id"] == resource_id), None)
    if not resource:
        return None
    available = resource["quantity"]
    extracted = min(amount, available)
    new_qty = max(0.0, available - extracted)
    await db.update_resource(resource_id, quantity=round(new_qty, 1), extraction_rate=extracted)
    if new_qty <= 0:
        await db.update_resource(resource_id, status="depleted")
    return {"extracted": round(extracted, 1), "remaining": round(new_qty, 1)}


async def regenerate_resources(planet_id: str) -> dict:
    from app.planetary import persistence as db
    resources = await db.list_resources(planet_id)
    regenerated = 0
    for res in resources:
        if res["renewable"] and res["regeneration_rate"] > 0 and res["quantity"] < res["max_quantity"]:
            new_qty = min(res["max_quantity"], res["quantity"] + res["regeneration_rate"])
            await db.update_resource(res["id"], quantity=round(new_qty, 1))
            regenerated += 1
    return {"regenerated": regenerated}


async def survey_resources(planet_id: str, region_id: str) -> list[dict]:
    from app.planetary import persistence as db
    resources = await db.list_resources(planet_id, region_id=region_id, discovered=False)
    for res in resources:
        if random.random() > 0.4:
            await db.update_resource(res["id"], discovered=True)
    return await db.list_resources(planet_id, region_id=region_id)


def get_state() -> dict:
    return {"initialized": True}
