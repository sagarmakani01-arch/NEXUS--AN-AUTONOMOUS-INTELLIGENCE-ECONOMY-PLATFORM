import json
import random

from app.genesis.persistence import genesis_db


AWARENESS_LEVELS = [
    {
        "level": 0,
        "name": "Unaware",
        "description": "No concept of an external creator. The world simply exists.",
    },
    {
        "level": 1,
        "name": "Unknown Force",
        "description": "Suspicion that unseen forces or spirits influence the world.",
    },
    {
        "level": 2,
        "name": "Intelligent Influence",
        "description": "Belief that some intelligent entity or entities shaped the world.",
    },
    {
        "level": 3,
        "name": "Advanced Understanding",
        "description": "Understanding that the universe follows discoverable rules and may have been designed.",
    },
    {
        "level": 4,
        "name": "Simulation Discovery",
        "description": "Discovery that their reality is a simulated construct.",
    },
]


class AwarenessEngine:
    async def tick(self, civ_id: str) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        if not civ:
            return {}

        current_level = civ["awareness_level"] or 0
        developments = []
        agents = await genesis_db.get_agents(civ_id)
        alive = [a for a in agents if a["status"] == "alive"]

        discoveries = await genesis_db.get_discoveries(civ_id)
        scientific_discs = [d for d in discoveries if d["discovery_type"] == "scientific"]

        if current_level < 1 and len(discoveries) >= 3:
            await self._advance_awareness(civ, 1, "The accumulation of knowledge suggests patterns that imply purpose.", alive)
            developments.append("awareness_level_1")

        if current_level < 2 and civ["scientific_level"] and civ["scientific_level"] > 0.2:
            await self._advance_awareness(civ, 2, "Natural laws seem too consistent to be accidental. Something must have set them in motion.", alive)
            developments.append("awareness_level_2")

        if current_level < 3 and civ["technology_level"] and civ["technology_level"] > 0.4 and len(scientific_discs) >= 3:
            await self._advance_awareness(civ, 3, "The universe operates on precise, mathematical principles that can be discovered and understood.", alive)
            developments.append("awareness_level_3")

        if current_level < 4 and civ["technology_level"] and civ["technology_level"] > 0.8 and len(scientific_discs) >= 8:
            await self._advance_awareness(civ, 4, "After centuries of inquiry, the philosophers and scientists have reached a startling conclusion: their reality may be a simulation.", alive)
            await genesis_db.update_civilization(civ["id"], has_discovered_simulation=1)
            developments.append("awareness_level_4")

        return {"developments": developments, "current_level": current_level}

    async def _advance_awareness(self, civ: dict, level: int, understanding: str, agents: list[dict]) -> None:
        await genesis_db.update_civilization(civ["id"], awareness_level=level)
        philosopher = random.choice(agents) if agents else None
        await genesis_db.create_awareness_record(
            civilization_id=civ["id"],
            awareness_level=level,
            understanding_description=understanding,
            evidence_collected=json.dumps(["Observation", "Scientific method", "Philosophical reasoning"]),
            philosopher_responsible=philosopher["name"] if philosopher else "unknown",
        )

    async def get_awareness_status(self, civ_id: str) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        if not civ:
            return {"level": 0, "description": "Civilization not found"}
        level = civ["awareness_level"] or 0
        records = await genesis_db.get_awareness_records(civ_id)
        return {
            "level": level,
            "label": AWARENESS_LEVELS[level]["name"] if level < len(AWARENESS_LEVELS) else "Unknown",
            "description": AWARENESS_LEVELS[level]["description"] if level < len(AWARENESS_LEVELS) else "",
            "has_discovered_simulation": bool(civ["has_discovered_simulation"]),
            "records": records,
        }


awareness_engine = AwarenessEngine()
