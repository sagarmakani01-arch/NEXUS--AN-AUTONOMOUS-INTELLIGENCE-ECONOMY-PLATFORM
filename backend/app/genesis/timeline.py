import random

from app.genesis.persistence import genesis_db


ERA_THRESHOLDS = {
    "settlement": {"tech": 0.1, "culture": 0.1, "min_year": 20},
    "agricultural": {"tech": 0.2, "culture": 0.15, "min_year": 50},
    "industrial": {"tech": 0.35, "culture": 0.25, "min_year": 100},
    "scientific": {"tech": 0.5, "culture": 0.35, "min_year": 200},
    "space": {"tech": 0.75, "culture": 0.5, "min_year": 400},
}

ERA_NAMES = ["primitive", "settlement", "agricultural", "industrial", "scientific", "space"]

ERA_TRANSITION_EVENTS = {
    "settlement": "The people built permanent dwellings and formed the first settlement.",
    "agricultural": "Agriculture was developed, allowing the population to grow and specialize.",
    "industrial": "Machines and industry transformed the civilization's capabilities.",
    "scientific": "The scientific method was embraced, leading to rapid knowledge growth.",
    "space": "The civilization reached beyond their world, exploring the cosmos.",
}


class TimelineEngine:
    async def tick(self, civ_id: str) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        if not civ:
            return {}

        current_year = (civ["current_year"] or 0) + 1
        current_era = civ["era"] or "primitive"
        events = []

        for next_era, threshold in ERA_THRESHOLDS.items():
            if current_era == "primitive" or ERA_NAMES.index(next_era) > ERA_NAMES.index(current_era):
                if (civ["technology_level"] or 0) >= threshold["tech"] and \
                   (civ["culture_level"] or 0) >= threshold["culture"] and \
                   current_year >= threshold["min_year"]:
                    await self._transition_era(civ, next_era, current_year)
                    events.append({
                        "type": "era_transition",
                        "from": current_era,
                        "to": next_era,
                        "year": current_year,
                        "description": ERA_TRANSITION_EVENTS.get(next_era, f"Entered the {next_era} era."),
                    })
                    current_era = next_era
                    break

        await genesis_db.update_civilization(
            civ["id"],
            current_year=current_year,
            era=current_era,
        )

        return {"current_year": current_year, "era": current_era, "events": events}

    async def _transition_era(self, civ: dict, new_era: str, year: int) -> None:
        await genesis_db.close_era(civ["id"], civ["era"] or "primitive", year)
        await genesis_db.create_era(
            civilization_id=civ["id"],
            era_name=new_era,
            start_year=year,
            population_at_start=civ["population"],
            technology_level=civ["technology_level"],
            culture_level=civ["culture_level"],
        )


timeline_engine = TimelineEngine()
