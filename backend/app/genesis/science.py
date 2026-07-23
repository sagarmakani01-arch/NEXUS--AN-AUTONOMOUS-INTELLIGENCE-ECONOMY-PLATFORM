import json
import random

from app.genesis.persistence import genesis_db


class ScienceEngine:
    async def tick(self, civ_id: str) -> dict:
        civ = await genesis_db.get_civilization(civ_id)
        if not civ:
            return {}

        discoveries = []

        if random.random() < 0.1:
            disc = await self._scientific_discovery(civ)
            if disc:
                discoveries.append(disc)

        tech_gain = 0.0
        sci_gain = 0.0
        agents = await genesis_db.get_agents(civ_id)
        for agent in agents:
            if agent["status"] != "alive":
                continue
            tech_gain += agent["intelligence_level"] * 0.001
            sci_gain += agent["survival_skill"] * 0.001

        new_tech = min(1.0, (civ["technology_level"] or 0) + tech_gain)
        new_sci = min(1.0, (civ["scientific_level"] or 0) + sci_gain)
        await genesis_db.update_civilization(civ["id"], technology_level=round(new_tech, 3), scientific_level=round(new_sci, 3))

        domains = await genesis_db.get_knowledge_domains(civ["id"])
        for domain in domains:
            gain = random.uniform(0.001, 0.01)
            new_level = min(1.0, (domain["level"] or 0) + gain)
            await genesis_db.update_knowledge(civ["id"], domain["domain_name"], level=round(new_level, 3))

        return {"discoveries": len(discoveries)}

    async def _scientific_discovery(self, civ: dict) -> dict | None:
        discoveries = [
            ("astronomy", "The stars are distant suns", "astronomy_cosmic_understanding", 0.3),
            ("physics", "Objects fall due to a force", "physics_gravity_concept", 0.2),
            ("biology", "Living things come from other living things", "biology_reproduction", 0.25),
            ("nature", "The seasons follow a regular cycle", "nature_seasonal_cycle", 0.3),
            ("tools", "Leverage can multiply force", "technology_lever", 0.2),
        ]
        disc = random.choice(discoveries)
        domain_name, understanding, disc_type, impact = disc

        existing = await genesis_db.get_knowledge_domains(civ["id"])
        has_domain = any(d["domain_name"] == domain_name for d in existing)
        if not has_domain:
            await genesis_db.get_or_create_knowledge(civ["id"], domain_name)

        await genesis_db.update_knowledge(civ["id"], domain_name, understanding=understanding, discoveries_made=1)

        discovery = await genesis_db.create_discovery(
            civilization_id=civ["id"],
            discovery_type="scientific",
            title=understanding,
            description=f"Through observation and reasoning, the {civ['name']} discovered that {understanding.lower()}.",
            impact_level=impact,
            era_recorded=civ["era"],
        )
        return discovery

    async def get_knowledge_summary(self, civ_id: str) -> dict:
        domains = await genesis_db.get_knowledge_domains(civ_id)
        civ = await genesis_db.get_civilization(civ_id)
        return {
            "domains": domains,
            "technology_level": civ["technology_level"] if civ else 0,
            "scientific_level": civ["scientific_level"] if civ else 0,
            "total_domains": len(domains),
        }


science_engine = ScienceEngine()
