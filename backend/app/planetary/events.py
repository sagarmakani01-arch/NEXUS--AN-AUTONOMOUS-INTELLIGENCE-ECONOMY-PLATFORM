import logging
import random

logger = logging.getLogger("nexus.planetary.events")

EVENT_TYPES = ["flood", "drought", "wildfire", "earthquake", "resource_discovery",
               "infrastructure_failure", "extreme_weather", "volcanic_activity"]


async def trigger_event(planet_id: str, event_type: str | None = None,
                        region_id: str | None = None) -> dict:
    from app.planetary import persistence as db
    if event_type not in EVENT_TYPES:
        event_type = random.choice(EVENT_TYPES)
    severity = random.uniform(1.0, 8.0)
    pop_affected = int(random.uniform(10, 500))
    res_damage = severity * random.uniform(5.0, 20.0)
    infra_damage = severity * random.uniform(2.0, 15.0)
    titles = {
        "flood": "Flash Flood", "drought": "Severe Drought",
        "wildfire": "Wildfire Outbreak", "earthquake": "Earthquake",
        "resource_discovery": "New Resource Discovery",
        "infrastructure_failure": "Infrastructure Failure",
        "extreme_weather": "Extreme Weather Event",
        "volcanic_activity": "Volcanic Activity",
    }
    eid = await db.create_env_event(
        planet_id=planet_id, event_type=event_type,
        region_id=region_id, title=titles.get(event_type, "Environmental Event"),
        description=f"A {event_type.replace('_', ' ')} occurred",
        severity=round(severity, 1), duration_days=random.randint(1, 30),
        affected_population=pop_affected,
        resource_damage=round(res_damage, 1),
        infrastructure_damage=round(infra_damage, 1),
    )
    return {"id": eid, "type": event_type, "severity": severity}


async def check_random_events(planet_id: str) -> list[dict]:
    triggered = []
    if random.random() > 0.85:
        result = await trigger_event(planet_id)
        triggered.append(result)
    return triggered


def get_state() -> dict:
    return {"event_types": EVENT_TYPES, "initialized": True}
