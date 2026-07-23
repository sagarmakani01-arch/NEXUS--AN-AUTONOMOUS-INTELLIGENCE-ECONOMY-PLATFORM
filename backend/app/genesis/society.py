import json
import random

from app.genesis.persistence import genesis_db


class SocietyEngine:
    async def tick(self, civ_id: str) -> dict:
        agents = await genesis_db.get_agents(civ_id)
        if not agents:
            return {"events": []}

        civ = await genesis_db.get_civilization(civ_id)
        events = []

        for agent in agents:
            if agent["status"] != "alive":
                continue
            action = random.random()
            if action < 0.25:
                result = await self._explore(agent)
                if result:
                    events.append(result)
            elif action < 0.45:
                result = await self._socialize(agent, agents)
                if result:
                    events.append(result)
            elif action < 0.65:
                result = await self._learn(agent, civ)
                if result:
                    events.append(result)
            elif action < 0.8:
                await self._rest(agent)
            else:
                event = await self._discover(agent, civ)
                if event:
                    events.append(event)

        population = len([a for a in agents if a["status"] == "alive"])
        await genesis_db.update_civilization(civ_id, population=population)

        return {"events": events}

    async def _explore(self, agent: dict) -> dict | None:
        gain = round(random.uniform(0.01, 0.05), 3)
        await genesis_db.update_agent(agent["id"], survival_skill=min(1.0, agent["survival_skill"] + gain))
        if random.random() < 0.3:
            return {"type": "exploration", "agent": agent["name"], "description": f"{agent['name']} explored new territory and found resources."}
        return None

    async def _socialize(self, agent: dict, agents: list[dict]) -> dict | None:
        others = [a for a in agents if a["id"] != agent["id"] and a["status"] == "alive"]
        if not others:
            return None
        other = random.choice(others)
        gain = round(random.uniform(0.01, 0.03), 3)
        await genesis_db.update_agent(agent["id"], social_influence=min(1.0, agent["social_influence"] + gain))
        if random.random() < 0.2:
            return {"type": "social", "agent": agent["name"], "other": other["name"], "description": f"{agent['name']} shared knowledge with {other['name']}."}
        return None

    async def _learn(self, agent: dict, civ: dict | None) -> dict | None:
        gain = round(random.uniform(0.01, 0.04), 3)
        await genesis_db.update_agent(agent["id"], intelligence_level=min(1.0, agent["intelligence_level"] + gain))
        if civ and random.random() < 0.15:
            cl = min(1.0, (civ.get("culture_level") or 0) + 0.02)
            await genesis_db.update_civilization(civ["id"], culture_level=cl)
            return {"type": "learning", "agent": agent["name"], "description": f"{agent['name']} taught the group a new skill."}
        return None

    async def _rest(self, agent: dict) -> None:
        await genesis_db.update_agent(agent["id"], energy=min(100.0, agent["energy"] + random.uniform(5, 15)))

    async def _discover(self, agent: dict, civ: dict | None) -> dict | None:
        if random.random() < 0.08:
            discoveries = [
                ("how to control fire", "technology", 0.4),
                ("that plants grow from seeds", "knowledge", 0.3),
                ("how to make basic tools from stone", "technology", 0.3),
                ("that stars move across the sky", "knowledge", 0.2),
                ("how to build simple shelters", "technology", 0.3),
                ("that some plants heal wounds", "knowledge", 0.3),
            ]
            disc = random.choice(discoveries)
            await genesis_db.create_discovery(
                civilization_id=civ["id"] if civ else agent["civilization_id"],
                discovery_type=disc[1],
                title=disc[0],
                description=f"{agent['name']} discovered {disc[0]}.",
                discoverer_agent_id=agent["id"],
                impact_level=disc[2],
                era_recorded="primitive",
            )
            count = agent["discovery_count"] + 1
            await genesis_db.update_agent(agent["id"], discovery_count=count)
            return {"type": "discovery", "agent": agent["name"], "title": disc[0], "description": f"{agent['name']} discovered {disc[0]}!"}
        return None


society_engine = SocietyEngine()
