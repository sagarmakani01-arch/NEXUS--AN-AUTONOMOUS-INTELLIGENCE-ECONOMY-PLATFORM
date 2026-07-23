from __future__ import annotations

import logging
import random

from app.organization import persistence as op

logger = logging.getLogger("nexus.organization.orgchart")

DEPARTMENT_TEMPLATES = {
    "technology": ["engineering", "product", "qa", "devops", "security"],
    "analytics": ["data", "business_intelligence", "research", "ml"],
    "finance": ["accounting", "treasury", "compliance", "audit"],
    "marketing": ["content", "growth", "brand", "social"],
    "creative": ["design", "content", "video", "ux"],
    "science": ["research", "development", "lab", "clinical"],
    "engineering": ["design", "production", "quality", "maintenance"],
    "healthcare": ["clinical", "admin", "research", "outreach"],
    "legal": ["corporate", "litigation", "compliance", "ip"],
    "logistics": ["operations", "supply_chain", "warehouse", "delivery"],
}


class OrgChart:
    async def initialize_departments(self, company_id: str, industry: str = "technology") -> list[dict]:
        depts = DEPARTMENT_TEMPLATES.get(industry, DEPARTMENT_TEMPLATES["technology"])
        departments = []
        for dept in depts:
            departments.append({
                "name": dept,
                "head_count": 0,
                "budget": 0,
                "status": "active",
            })
        await op.update_company(company_id, departments=departments)
        return departments

    async def get_org_chart(self, company_id: str) -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}

        members = await op.get_members(company_id)
        departments = company.get("departments", [])
        if isinstance(departments, str):
            import json
            try:
                departments = json.loads(departments)
            except (json.JSONDecodeError, TypeError):
                departments = []

        ceo = next((m for m in members if m["role"] == "c_level"), None)
        vps = [m for m in members if m["role"] == "vp"]
        directors = [m for m in members if m["role"] == "director"]
        managers = [m for m in members if m["role"] == "manager"]
        leads = [m for m in members if m["role"] == "lead"]
        employees = [m for m in members if m["role"] in ("employee", "senior")]

        dept_members = {}
        for m in members:
            dept = m.get("department", "unassigned")
            dept_members.setdefault(dept, []).append(m)

        return {
            "company_id": company_id,
            "ceo": ceo,
            "vps": vps,
            "directors": directors,
            "managers": managers,
            "leads": leads,
            "employees": employees,
            "departments": departments,
            "department_members": dept_members,
            "total_members": len(members),
        }

    async def assign_department_head(self, company_id: str, agent_id: str, department: str) -> dict:
        members = await op.get_members(company_id)
        existing_head = next((m for m in members if m.get("department") == department and m["role"] == "manager"), None)
        if existing_head:
            await op.update_member(existing_head["id"], role="lead")

        member = next((m for m in members if m["agent_id"] == agent_id), None)
        if not member:
            return {"error": "Agent not in company"}
        result = await op.update_member(member["id"], role="manager", department=department, title=f"{department.title()} Manager")
        await op.add_memory(
            company_id, "department_head_assigned",
            f"{department.title()} head assigned",
            f"Agent {agent_id} assigned as {department} manager",
            "medium",
        )
        return result or member

    async def get_department_info(self, company_id: str, department: str) -> dict:
        members = await op.get_members(company_id)
        dept_members = [m for m in members if m.get("department") == department]
        total_salary = sum(m["salary"] for m in dept_members)
        avg_performance = sum(m["performance_score"] for m in dept_members) / max(len(dept_members), 1)
        return {
            "department": department,
            "member_count": len(dept_members),
            "members": dept_members,
            "total_salary": round(total_salary, 2),
            "avg_performance": round(avg_performance, 1),
        }


org_chart = OrgChart()
