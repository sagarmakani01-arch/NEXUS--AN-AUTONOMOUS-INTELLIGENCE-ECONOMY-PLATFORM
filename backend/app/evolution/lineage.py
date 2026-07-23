import logging
import random

from app.evolution import persistence as evo_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.evolution.lineage")


class LineageSystem:
    def __init__(self):
        self.stats = {
            "lineages_created": 0,
            "lineages_merged": 0,
        }

    async def create_lineage(self, founder_agent_id: str, name: str | None = None,
                             parent_lineage_id: str | None = None) -> dict:
        if not name:
            name = f"Lineage-{random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta'])}-{random.randint(100, 999)}"

        from app.simulation.engine import engine as sim_engine
        profile = sim_engine.profiles.get(founder_agent_id)
        trait_profile = {}
        if profile:
            trait_profile = profile.personality

        lineage_id = await evo_db.create_lineage(
            name=name, founder_agent_id=founder_agent_id,
            parent_lineage_id=parent_lineage_id,
            trait_profile=trait_profile,
        )
        self.stats["lineages_created"] += 1

        await dispatch(Event(EventType.LINEAGE_CREATED, {
            "lineage_id": lineage_id, "name": name,
            "founder_agent_id": founder_agent_id,
        }))

        return {
            "lineage_id": lineage_id,
            "name": name,
            "founder_agent_id": founder_agent_id,
        }

    async def get_lineage(self, lineage_id: str) -> dict | None:
        return await evo_db.get_lineage(lineage_id)

    async def list_lineages(self) -> list[dict]:
        return await evo_db.list_lineages()

    async def add_member(self, lineage_id: str, agent_id: str) -> dict:
        lineage = await evo_db.get_lineage(lineage_id)
        if not lineage:
            return {"success": False, "error": "Lineage not found"}

        from app.simulation.engine import engine as sim_engine
        profile = sim_engine.profiles.get(agent_id)
        if not profile:
            return {"success": False, "error": "Agent not found"}

        new_count = lineage["member_count"] + 1
        new_rep = ((lineage["average_reputation"] * lineage["member_count"]) +
                   profile.agent.reputation) / new_count

        skills = profile.skills
        avg_skill = sum(s.get("level", 1) for s in skills) / max(len(skills), 1)
        new_avg_skill = ((lineage["average_skill_level"] * lineage["member_count"]) +
                         avg_skill) / new_count

        await evo_db.update_lineage(
            lineage_id,
            member_count=new_count,
            average_reputation=round(new_rep, 2),
            average_skill_level=round(new_avg_skill, 2),
        )
        return {"success": True, "lineage_id": lineage_id, "new_member_count": new_count}

    async def get_lineage_tree(self, lineage_id: str) -> dict:
        lineage = await evo_db.get_lineage(lineage_id)
        if not lineage:
            return {}

        children = []
        all_lineages = await evo_db.list_lineages()
        for l in all_lineages:
            if l.get("parent_lineage_id") == lineage_id:
                children.append(l)

        return {
            "lineage": lineage,
            "children": children,
            "depth": len(children),
        }

    async def get_lineage_performance(self, lineage_id: str) -> dict:
        lineage = await evo_db.get_lineage(lineage_id)
        if not lineage:
            return {}

        generations = await evo_db.list_generations(lineage_id)
        innovations = await evo_db.list_innovations()
        lineage_innovations = [i for i in innovations if i.get("lineage_id") == lineage_id]

        return {
            "lineage_id": lineage_id,
            "name": lineage["name"],
            "member_count": lineage["member_count"],
            "generation_count": lineage["generation_count"],
            "average_reputation": lineage["average_reputation"],
            "average_skill_level": lineage["average_skill_level"],
            "total_innovations": len(lineage_innovations),
            "generations": generations[:5],
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


lineage_system = LineageSystem()
