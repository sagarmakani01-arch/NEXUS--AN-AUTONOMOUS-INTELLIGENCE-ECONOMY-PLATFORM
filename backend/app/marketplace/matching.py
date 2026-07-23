from __future__ import annotations

import logging
import random

from app.marketplace import persistence as mp

logger = logging.getLogger("nexus.marketplace.matching")


class MatchingEngine:
    def score_agent_for_task(self, agent_skills: list[str], task_skills: list[str], agent_reputation: float = 0, agent_energy: float = 100) -> float:
        if not task_skills:
            skill_score = 1.0
        else:
            matched = len(set(agent_skills) & set(task_skills))
            skill_score = matched / len(task_skills) if task_skills else 0
        rep_score = min(agent_reputation / 2.0, 1.0)
        energy_score = agent_energy / 100.0
        return round(skill_score * 0.5 + rep_score * 0.3 + energy_score * 0.2, 3)

    async def find_opportunities(self, agent_skills: list[str], agent_reputation: float = 50, agent_energy: float = 100, limit: int = 10) -> list[dict]:
        tasks = await mp.list_tasks(status="open")
        scored = []
        for task in tasks:
            score = self.score_agent_for_task(agent_skills, task.get("required_skills", []), agent_reputation, agent_energy)
            if score > 0.2:
                scored.append({**task, "match_score": score})
        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored[:limit]

    async def find_best_agents_for_task(self, task_id: str, all_agents: list[dict], limit: int = 5) -> list[dict]:
        task = await mp.get_task(task_id)
        if not task:
            return []
        task_skills = task.get("required_skills", [])
        scored = []
        for agent in all_agents:
            score = self.score_agent_for_task(
                agent.get("skills", []), task_skills,
                agent.get("reputation", 0), agent.get("energy", 100),
            )
            if score > 0.1:
                scored.append({**agent, "match_score": score})
        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored[:limit]

    async def match_all(self, all_agents: list[dict], limit_per_agent: int = 5) -> dict[str, list[dict]]:
        matches = {}
        for agent in all_agents:
            opportunities = await self.find_opportunities(
                agent.get("skills", []),
                agent.get("reputation", 0),
                agent.get("energy", 100),
                limit_per_agent,
            )
            if opportunities:
                matches[agent["id"]] = opportunities
        return matches


matching_engine = MatchingEngine()
