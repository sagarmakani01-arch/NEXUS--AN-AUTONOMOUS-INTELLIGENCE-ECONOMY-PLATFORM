from __future__ import annotations

import json
import logging
import random
from typing import Any

from app.organization import persistence as op

logger = logging.getLogger("nexus.organization.hiring")

SALARY_RANGES = {
    "technology": {"engineer": (60, 150), "manager": (100, 200), "lead": (120, 250)},
    "analytics": {"analyst": (50, 120), "scientist": (80, 180), "director": (130, 250)},
    "finance": {"analyst": (60, 130), "manager": (100, 200), "director": (150, 300)},
    "marketing": {"coordinator": (40, 90), "manager": (80, 160), "director": (120, 230)},
    "creative": {"designer": (45, 100), "lead": (80, 160), "director": (110, 210)},
    "science": {"researcher": (55, 120), "lead": (90, 180), "director": (130, 250)},
    "engineering": {"engineer": (60, 130), "lead": (100, 200), "director": (140, 270)},
    "healthcare": {"practitioner": (70, 150), "specialist": (110, 220), "director": (160, 300)},
    "legal": {"associate": (65, 140), "counsel": (110, 220), "partner": (180, 350)},
    "logistics": {"coordinator": (40, 90), "manager": (80, 160), "director": (120, 230)},
}

ROLE_HIERARCHY = ["employee", "senior", "lead", "manager", "director", "vp", "c_level"]
DEPARTMENTS = ["engineering", "product", "design", "marketing", "sales", "finance", "hr", "operations", "research", "legal"]


class HiringEngine:
    async def create_job_opening(
        self, company_id: str, title: str, department: str = "",
        required_skills: list[str] | None = None, salary_range: str = "",
        description: str = "",
    ) -> dict:
        opening = {
            "company_id": company_id,
            "title": title,
            "department": department or random.choice(DEPARTMENTS),
            "required_skills": required_skills or [],
            "salary_range": salary_range,
            "description": description,
            "status": "open",
        }
        await op.add_memory(
            company_id, "job_opening",
            f"New opening: {title}",
            f"Department: {department}, Skills: {', '.join(required_skills or [])}",
            "medium",
        )
        logger.info("job_opening_created company=%s title=%s", company_id, title)
        return opening

    async def find_candidates(
        self, company_id: str, required_skills: list[str],
        all_agents: list[dict], limit: int = 10,
    ) -> list[dict]:
        candidates = []
        for agent in all_agents:
            agent_skills = set(agent.get("skills", []))
            skill_overlap = len(agent_skills & set(required_skills))
            if skill_overlap == 0:
                continue
            reputation = agent.get("reputation", 0)
            energy = agent.get("energy", 100)
            score = (skill_overlap / max(len(required_skills), 1)) * 0.5 + min(reputation / 2, 1) * 0.3 + (energy / 100) * 0.2
            candidates.append({
                **agent,
                "match_score": round(score, 3),
                "skill_overlap": skill_overlap,
            })
        candidates.sort(key=lambda x: x["match_score"], reverse=True)
        return candidates[:limit]

    async def interview_candidate(self, agent_id: str, company_id: str, agent_personality: dict | None = None) -> dict:
        personality = agent_personality or {}
        conscientiousness = personality.get("conscientiousness", 0.5)
        agreeableness = personality.get("agreeableness", 0.5)
        extraversion = personality.get("extraversion", 0.5)

        technical_score = round(conscientiousness * 0.6 + random.uniform(0.2, 0.4), 2)
        cultural_score = round(agreeableness * 0.5 + extraversion * 0.3 + random.uniform(0.1, 0.3), 2)
        overall = round(technical_score * 0.6 + cultural_score * 0.4, 2)

        recommendation = "hire" if overall > 0.5 else "consider" if overall > 0.3 else "reject"
        return {
            "agent_id": agent_id,
            "company_id": company_id,
            "technical_score": technical_score,
            "cultural_fit_score": cultural_score,
            "overall_score": overall,
            "recommendation": recommendation,
        }

    async def negotiate_salary(self, company_id: str, agent_id: str, industry: str = "", role: str = "employee") -> dict:
        ranges = SALARY_RANGES.get(industry, SALARY_RANGES["technology"])
        role_range = ranges.get(role, (50, 120))
        company = await op.get_company(company_id)
        budget_factor = min(company.get("treasury_balance", 100) / 1000, 1.5) if company else 1.0
        base = random.uniform(role_range[0], role_range[1]) * budget_factor
        company_offer = round(base * 0.9, 2)
        agent_expected = round(base * random.uniform(0.95, 1.15), 2)
        final = round((company_offer + agent_expected) / 2, 2)
        return {
            "company_offer": company_offer,
            "agent_expected": agent_expected,
            "agreed_salary": final,
            "role": role,
            "industry": industry,
        }

    async def hire_agent(
        self, company_id: str, agent_id: str, role: str = "employee",
        department: str = "", title: str = "", salary: float = 0,
        reports_to: str | None = None,
    ) -> dict:
        result = await op.add_member(
            company_id=company_id, agent_id=agent_id,
            role=role, department=department, title=title,
            salary=salary, reports_to=reports_to,
        )
        if "error" in result:
            return result
        await op.add_memory(
            company_id, "employee_hired",
            f"Hired: {title or role}",
            f"Agent {agent_id} joined as {role} in {department}",
            "high",
        )
        logger.info("agent_hired company=%s agent=%s role=%s", company_id, agent_id, role)
        return result

    async def fire_agent(self, company_id: str, agent_id: str, reason: str = "") -> dict:
        result = await op.remove_member(company_id, agent_id)
        if not result:
            return {"error": "Member not found"}
        await op.add_memory(
            company_id, "employee_removed",
            f"Removed agent: {agent_id}",
            f"Reason: {reason}" if reason else "No reason specified",
            "high",
        )
        logger.info("agent_fired company=%s agent=%s reason=%s", company_id, agent_id, reason)
        return result

    async def promote_agent(self, company_id: str, agent_id: str, new_role: str, new_title: str = "") -> dict:
        members = await op.get_members(company_id)
        member = next((m for m in members if m["agent_id"] == agent_id), None)
        if not member:
            return {"error": "Member not found"}
        result = await op.update_member(member["id"], role=new_role, title=new_title or new_role)
        await op.add_memory(
            company_id, "employee_promoted",
            f"Promoted to {new_role}",
            f"Agent {agent_id} promoted from {member['role']} to {new_role}",
            "high",
        )
        return result or member


hiring_engine = HiringEngine()
