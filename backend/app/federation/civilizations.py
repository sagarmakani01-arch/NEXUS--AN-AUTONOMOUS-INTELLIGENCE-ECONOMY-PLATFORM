import json
import logging
import random

from app.federation import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.federation.civilizations")

CIV_NAMES = [
    "Aethoria", "Borealis", "Cyberia", "Dawnreach", "Elysium",
    "Fortuna", "Gehenna", "Helion", "Ignisia", "Jovia",
]
DEFAULT_VALUES = ["innovation", "tradition", "efficiency", "freedom", "knowledge", "prosperity"]
GOVERNMENT_TYPES = ["centralized", "distributed", "experimental", "democratic", "meritocratic"]
ECONOMIC_MODELS = ["free_market", "resource_controlled", "research_focused", "planned", "mixed"]


class CivilizationManager:
    def __init__(self):
        self.stats = {"created": 0, "total_population": 0}

    async def create_civilization(self, name: str | None = None,
                                  leader_agent_id: str | None = None,
                                  government_type: str | None = None,
                                  economic_model: str | None = None,
                                  population: int = 0) -> dict:
        name = name or random.choice(CIV_NAMES) + f"-{random.randint(100, 999)}"
        gov = government_type or random.choice(GOVERNMENT_TYPES)
        econ = economic_model or random.choice(ECONOMIC_MODELS)
        values = random.sample(DEFAULT_VALUES, k=3)

        civ_id = await db.create_civilization(
            name=name, leader_agent_id=leader_agent_id,
            population=population or random.randint(50, 200),
            technology_level=round(random.uniform(0.5, 2.0), 2),
            economic_power=round(random.uniform(30, 80), 1),
            military_strength=round(random.uniform(10, 50), 1),
            cultural_influence=round(random.uniform(20, 60), 1),
            government_type=gov, economic_model=econ,
            values=json.dumps({v: random.uniform(0.3, 1.0) for v in values}),
            priorities=json.dumps(values[:2]),
        )
        await db.create_rules(civilization_id=civ_id,
                              economic_model=econ, governance_type=gov)
        await db.record_history(civ_id, "founding", f"{name} founded",
                                f"A new civilization with {gov} governance and {econ} economy")
        self.stats["created"] += 1
        self.stats["total_population"] += population or 100

        await dispatch(Event(EventType.CIVILIZATION_CREATED, {
            "civilization_id": civ_id, "name": name,
            "government": gov, "economic_model": econ,
        }))
        return {"civilization_id": civ_id, "name": name, "government": gov, "economic_model": econ}

    async def get_civilization(self, civ_id: str) -> dict | None:
        return await db.get_civilization(civ_id)

    async def list_civilizations(self) -> list[dict]:
        return await db.list_civilizations()

    async def update_civilization(self, civ_id: str, **kwargs) -> dict:
        await db.update_civilization(civ_id, **kwargs)
        return {"success": True}

    async def tick_civilization(self, civ_id: str) -> dict:
        civ = await db.get_civilization(civ_id)
        if not civ:
            return {}

        pop_change = random.randint(-2, 5)
        new_pop = max(10, civ["population"] + pop_change)
        econ_change = random.uniform(-2, 3)
        tech_change = random.uniform(-0.05, 0.1)
        happy_change = random.uniform(-3, 3)

        new_econ = max(0, min(100, civ["economic_power"] + econ_change))
        new_tech = max(0.1, min(10, civ["technology_level"] + tech_change))
        new_happy = max(0, min(100, civ["happiness"] + happy_change))
        new_rep = max(0, min(100, civ["reputation"] + random.uniform(-1, 1)))

        await db.update_civilization(
            civ_id, population=new_pop,
            economic_power=round(new_econ, 1),
            technology_level=round(new_tech, 2),
            happiness=round(new_happy, 1),
            reputation=round(new_rep, 1),
        )
        return {"population": new_pop, "economic_power": round(new_econ, 1),
                "technology_level": round(new_tech, 2)}

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


civilization_manager = CivilizationManager()
