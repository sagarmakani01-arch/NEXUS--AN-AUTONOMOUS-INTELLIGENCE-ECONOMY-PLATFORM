import json
import random

from app.genesis.persistence import genesis_db


SCHOOLS = [
    "empiricism", "rationalism", "stoicism", "existentialism",
    "naturalism", "dualism", "skepticism", "pragmatism",
]

PHILOSOPHY_TEMPLATES = [
    {
        "name": "The Observers",
        "ideas": [
            "Truth is discovered through observation of the natural world.",
            "Knowledge comes from experience, not from spirits.",
            "The world follows patterns that can be understood.",
        ],
    },
    {
        "name": "The Questioners",
        "ideas": [
            "Nothing can be known with certainty.",
            "All beliefs must be questioned.",
            "The nature of existence is the fundamental question.",
        ],
    },
    {
        "name": "The Harmonists",
        "ideas": [
            "Balance between all forces is the highest good.",
            "The individual and the community must be in harmony.",
            "Conflict arises from imbalance, not from evil.",
        ],
    },
    {
        "name": "The Materialists",
        "ideas": [
            "Only the physical world is real.",
            "Spirits and gods are explanations for what we do not understand.",
            "The universe operates by natural laws.",
        ],
    },
    {
        "name": "The Transcedents",
        "ideas": [
            "There is a reality beyond the physical world.",
            "The material world is a shadow of a greater truth.",
            "Understanding requires looking beyond appearances.",
        ],
    },
]


class PhilosophyEngine:
    async def tick(self, civ_id: str) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        if not civ:
            return {}
        philosophies = await genesis_db.get_philosophies(civ_id)
        agents = await genesis_db.get_agents(civ_id)

        if not philosophies and civ["culture_level"] > 0.15:
            alive = [a for a in agents if a["status"] == "alive"]
            if alive:
                return await self._emerge_philosophy(civ, random.choice(alive))

        if philosophies and random.random() < 0.03:
            phil = random.choice(philosophies)
            new_influence = min(1.0, phil["influence"] + 0.02)
            await genesis_db.update_philosophy(phil["id"], influence=round(new_influence, 3))

        return {"philosophies_count": len(philosophies)}

    async def _emerge_philosophy(self, civ: dict, agent: dict) -> dict:
        template = random.choice(PHILOSOPHY_TEMPLATES)
        school = random.choice(SCHOOLS)
        phil = await genesis_db.create_philosophy(
            civilization_id=civ["id"],
            name=f"{template['name']} of {agent['name']}",
            philosopher_agent_id=agent["id"],
            school_of_thought=school,
            core_ideas=json.dumps(template["ideas"]),
            influence=0.1,
            followers=random.randint(1, 3),
            status="emerging",
        )
        awareness = civ["awareness_level"] or 0
        if school in ["rationalism", "skepticism", "empiricism"] and random.random() < 0.3:
            new_level = min(4, awareness + 1)
            await self._update_awareness(civ["id"], new_level, agent, phil)

        return {"new_philosophy": phil}

    async def _update_awareness(self, civ_id: str, level: int, agent: dict, phil: dict) -> None:
        await genesis_db.update_civilization(civ_id, awareness_level=level)
        await genesis_db.create_awareness_record(
            civilization_id=civ_id,
            awareness_level=level,
            understanding_description=f"{agent['name']} proposed that the world might be understood through reason and observation, questioning traditional beliefs.",
            evidence_collected=json.dumps(["Philosophical reasoning", "Natural observation"]),
            philosopher_responsible=agent["name"],
        )


philosophy_engine = PhilosophyEngine()
