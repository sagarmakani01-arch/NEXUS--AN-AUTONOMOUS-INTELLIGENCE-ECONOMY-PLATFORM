import json
import random

from app.genesis.persistence import genesis_db


AGENT_NAMES = [
    "Aran", "Bera", "Cael", "Dorn", "Eira", "Fynn", "Gren", "Hael",
    "Iris", "Jorn", "Kael", "Lira", "Morn", "Nira", "Orin", "Pael",
    "Quin", "Rael", "Sorn", "Tira", "Ulin", "Vorn", "Wira", "Xael",
]

AGENT_ROLES = ["explorer", "hunter", "builder", "gatherer", "storyteller"]


class GenesisInitializer:
    async def create_civilization(self, name: str) -> dict:
        civ = await genesis_db.create_civilization(
            name=name,
            population=6,
            era="primitive",
            creation_year=0,
            current_year=0,
            origin_story=(
                f"In the beginning, there was nothing but the harsh wilderness. "
                f"A small group of {random.randint(4, 8)} beings awoke without memory of how they came to be. "
                f"They called themselves the {name}. "
                f"With no tools, no shelter, and no understanding of their world, "
                f"they began their struggle for survival."
            ),
        )
        await genesis_db.create_era(
            civilization_id=civ["id"],
            era_name="primitive",
            start_year=0,
            population_at_start=civ["population"],
            technology_level=0.0,
            culture_level=0.0,
        )
        for domain in ["nature", "fire", "tools", "shelter", "social"]:
            await genesis_db.get_or_create_knowledge(civ["id"], domain)
        await self._spawn_agents(civ["id"])
        return civ

    async def _spawn_agents(self, civ_id: str) -> list[dict]:
        agents = []
        for i in range(6):
            agent = await genesis_db.create_agent(
                civilization_id=civ_id,
                name=random.choice(AGENT_NAMES),
                role=random.choice(AGENT_ROLES),
                status="alive",
                intelligence_level=round(random.uniform(0.2, 0.5), 2),
                survival_skill=round(random.uniform(0.2, 0.6), 2),
                learning_rate=round(random.uniform(0.05, 0.2), 2),
                social_influence=round(random.uniform(0.1, 0.3), 2),
                energy=100.0,
                knowledge_areas=json.dumps(["basic_observation"]),
            )
            agents.append(agent)
        return agents


genesis_init = GenesisInitializer()
