import json
import logging
import random
import uuid

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.research_agents")


DEFAULT_AGENTS = [
    {"name": "Economist Alpha", "specialization": "economic", "laboratory_id": None},
    {"name": "Economist Beta", "specialization": "economic", "laboratory_id": None},
    {"name": "Climate Scientist Gamma", "specialization": "environmental", "laboratory_id": None},
    {"name": "Climate Scientist Delta", "specialization": "environmental", "laboratory_id": None},
    {"name": "Evolution Researcher Epsilon", "specialization": "evolution", "laboratory_id": None},
    {"name": "Evolution Researcher Zeta", "specialization": "evolution", "laboratory_id": None},
    {"name": "Technology Analyst Eta", "specialization": "technology", "laboratory_id": None},
    {"name": "Technology Analyst Theta", "specialization": "technology", "laboratory_id": None},
    {"name": "Social Researcher Iota", "specialization": "social", "laboratory_id": None},
    {"name": "Governance Analyst Kappa", "specialization": "governance", "laboratory_id": None},
]


async def initialize_agents():
    existing = await db.list_research_agents()
    if existing:
        return existing
    created = []
    for agent_data in DEFAULT_AGENTS:
        agent = await db.create_research_agent(**agent_data)
        created.append(agent)
    return created


async def assign_agents_to_labs():
    agents = await db.list_research_agents()
    labs = await db.list_laboratories()

    lab_map: dict[str, list[dict]] = {}
    for lab in labs:
        lab_map.setdefault(lab.get("lab_type", ""), []).append(lab)

    for agent in agents:
        spec = agent.get("specialization", "")
        if agent.get("laboratory_id"):
            continue
        matching_labs = lab_map.get(spec, [])
        if matching_labs:
            lab = random.choice(matching_labs)
            await db.update_research_agent(agent["id"], laboratory_id=lab["id"])

    return await db.list_research_agents()


async def agent_tick() -> list[dict]:
    agents = await db.list_research_agents()
    results = []
    for agent in agents:
        if agent.get("status") != "active":
            continue
        action = random.choice(["experiment", "pattern_analysis", "report"])
        result = await _perform_action(agent, action)
        results.append(result)
    return results


async def _perform_action(agent: dict, action: str) -> dict:
    if action == "experiment":
        await db.update_research_agent(agent["id"], experiments_conducted=agent.get("experiments_conducted", 0) + 1)
    elif action == "pattern_analysis":
        await db.update_research_agent(agent["id"], patterns_discovered=agent.get("patterns_discovered", 0) + 1)
    elif action == "report":
        await db.update_research_agent(agent["id"], reports_written=agent.get("reports_written", 0) + 1)

    return {
        "agent_id": agent["id"],
        "agent_name": agent["name"],
        "action": action,
        "specialization": agent.get("specialization", ""),
    }
