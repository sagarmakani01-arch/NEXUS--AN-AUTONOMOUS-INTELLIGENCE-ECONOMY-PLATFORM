from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.execution import persistence as ep

logger = logging.getLogger("nexus.execution.capabilities")

LEVEL_HIERARCHY = ["beginner", "intermediate", "advanced", "expert"]
LEVEL_THRESHOLDS = {
    "beginner": 0,
    "intermediate": 25,
    "advanced": 50,
    "expert": 75,
}


class AgentCapabilitySystem:
    async def init_capabilities(self, agent_id: str, skills: list[dict]) -> list[dict]:
        existing = await ep.get_capabilities(agent_id)
        existing_names = {c["skill_name"] for c in existing}
        created = []
        for skill in skills:
            name = skill.get("skill_name", skill.get("name", ""))
            if name and name not in existing_names:
                level = self._initial_level(skill.get("level", 1))
                cap = await ep.create_capability(
                    agent_id=agent_id, skill_name=name,
                    level=level, proficiency=min(skill.get("level", 1) * 10, 100),
                )
                created.append(cap)
        return created

    async def match_task_to_agent(self, task_skills: list[str], agent_id: str) -> float:
        caps = await ep.get_capabilities(agent_id)
        if not caps or not task_skills:
            return 0.0
        cap_map = {c["skill_name"]: c for c in caps}
        scores = []
        for skill in task_skills:
            cap = cap_map.get(skill)
            if cap:
                level_idx = LEVEL_HIERARCHY.index(cap["level"]) if cap["level"] in LEVEL_HIERARCHY else 0
                scores.append((level_idx + 1) / len(LEVEL_HIERARCHY))
            else:
                scores.append(0.0)
        return round(sum(scores) / len(scores), 3) if scores else 0

    async def find_best_agents(self, task_skills: list[str], agent_ids: list[str], limit: int = 5) -> list[dict]:
        scored = []
        for agent_id in agent_ids:
            score = await self.match_task_to_agent(task_skills, agent_id)
            if score > 0:
                caps = await ep.get_capabilities(agent_id)
                scored.append({
                    "agent_id": agent_id,
                    "match_score": score,
                    "capabilities": caps,
                })
        scored.sort(key=lambda x: x["match_score"], reverse=True)
        return scored[:limit]

    async def update_after_task(self, agent_id: str, skill_name: str, success: bool, duration: float = 0) -> dict:
        caps = await ep.get_capabilities(agent_id)
        cap = next((c for c in caps if c["skill_name"] == skill_name), None)
        if not cap:
            cap = await ep.create_capability(agent_id=agent_id, skill_name=skill_name)
        
        exp_gain = 10 if success else 3
        new_exp = cap["experience"] + exp_gain
        new_projects = cap["projects_completed"] + 1
        total_attempts = new_projects
        successes = int(cap["success_rate"] * cap["projects_completed"]) + (1 if success else 0)
        new_success_rate = successes / max(total_attempts, 1)
        new_level = self._calculate_level(new_exp)
        proficiency = min(new_exp, 100)

        updated = await ep.update_capability(
            cap["id"],
            experience=new_exp,
            projects_completed=new_projects,
            success_rate=round(new_success_rate, 2),
            level=new_level,
            proficiency=proficiency,
            last_used=datetime.now(timezone.utc),
        )
        if new_level != cap["level"]:
            logger.info("skill_leveled_up agent=%s skill=%s %s->%s", agent_id, skill_name, cap["level"], new_level)
        return updated or cap

    async def get_agent_profile(self, agent_id: str) -> dict:
        caps = await ep.get_capabilities(agent_id)
        total_proficiency = sum(c["proficiency"] for c in caps) / max(len(caps), 1)
        avg_success = sum(c["success_rate"] for c in caps) / max(len(caps), 1)
        return {
            "agent_id": agent_id,
            "capabilities": caps,
            "total_skills": len(caps),
            "avg_proficiency": round(total_proficiency, 1),
            "avg_success_rate": round(avg_success, 2),
            "expert_skills": len([c for c in caps if c["level"] == "expert"]),
            "advanced_skills": len([c for c in caps if c["level"] == "advanced"]),
        }

    async def get_all_capabilities(self) -> dict[str, list[dict]]:
        from sqlalchemy import select
        from app.core.database import async_session_factory
        from app.domain.models.agent_capability import AgentCapability
        async with async_session_factory() as session:
            result = await session.execute(select(AgentCapability))
            caps = result.scalars().all()
        agent_caps: dict[str, list[dict]] = {}
        for cap in caps:
            agent_caps.setdefault(cap.agent_id, []).append({
                "skill_name": cap.skill_name,
                "level": cap.level,
                "proficiency": cap.proficiency,
            })
        return agent_caps

    def _initial_level(self, sim_level: int) -> str:
        if sim_level >= 5:
            return "advanced"
        elif sim_level >= 3:
            return "intermediate"
        return "beginner"

    def _calculate_level(self, experience: float) -> str:
        if experience >= 75:
            return "expert"
        elif experience >= 50:
            return "advanced"
        elif experience >= 25:
            return "intermediate"
        return "beginner"


capability_system = AgentCapabilitySystem()
