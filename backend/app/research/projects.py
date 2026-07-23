import json
import logging
import random

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.projects")

RESEARCH_DOMAINS = [
    "Artificial Intelligence", "Quantum Computing", "Biotechnology",
    "Materials Science", "Neuroscience", "Climate Science",
    "Economics", "Computer Science", "Physics", "Medicine",
]

PROJECT_TEMPLATES = [
    {"title": "Advanced {domain} Framework", "question": "How can {domain} be improved through novel approaches?"},
    {"title": "Scalable {domain} Solutions", "question": "What are the limits of current {domain} methods?"},
    {"title": "Cross-disciplinary {domain} Study", "question": "How does {domain} interact with emerging technologies?"},
    {"title": "Optimization of {domain} Processes", "question": "Can {domain} efficiency be significantly improved?"},
    {"title": "Foundational {domain} Research", "question": "What are the fundamental principles underlying {domain}?"},
]


class ProjectManager:
    def __init__(self):
        self.stats = {
            "projects_created": 0,
            "projects_completed": 0,
            "projects_failed": 0,
        }

    async def create_project(self, title: str, research_question: str,
                             lead_agent_id: str | None = None,
                             organization_id: str | None = None,
                             hypothesis: str | None = None,
                             required_skills: list[str] | None = None,
                             budget: float = 100,
                             timeline_days: int = 30,
                             knowledge_domain: str | None = None,
                             priority: str = "medium") -> dict:
        if not knowledge_domain:
            knowledge_domain = random.choice(RESEARCH_DOMAINS)
        if not required_skills:
            required_skills = random.sample(
                ["Research Methods", "Data Analysis", "Scientific Writing",
                 "Statistical Analysis", "Machine Learning", "Software Development"],
                k=min(3, 6),
            )
        project_id = await db.create_project(
            title=title, research_question=research_question,
            lead_agent_id=lead_agent_id, organization_id=organization_id,
            hypothesis=hypothesis or f"Novel approaches in {knowledge_domain} will yield measurable improvements",
            required_skills=json.dumps(required_skills),
            budget=budget, timeline_days=timeline_days,
            knowledge_domain=knowledge_domain, priority=priority,
        )
        self.stats["projects_created"] += 1

        if organization_id:
            org = await db.get_organization(organization_id)
            if org:
                await db.update_organization(
                    organization_id,
                    total_projects=org.get("total_projects", 0) + 1,
                )

        await dispatch(Event(EventType.RESEARCH_STARTED, {
            "project_id": project_id, "title": title,
            "domain": knowledge_domain, "organization_id": organization_id,
        }))

        return {
            "project_id": project_id, "title": title,
            "domain": knowledge_domain, "budget": budget,
            "timeline_days": timeline_days,
        }

    async def auto_generate_project(self, organization_id: str | None = None) -> dict:
        domain = random.choice(RESEARCH_DOMAINS)
        template = random.choice(PROJECT_TEMPLATES)
        return await self.create_project(
            title=template["title"].format(domain=domain),
            research_question=template["question"].format(domain=domain),
            organization_id=organization_id,
            knowledge_domain=domain,
        )

    async def progress_project(self, project_id: str) -> dict:
        project = await db.get_project(project_id)
        if not project:
            return {"success": False, "error": "Project not found"}
        if project["status"] not in ("active", "proposed"):
            return {"success": False, "error": f"Cannot progress project in status: {project['status']}"}

        progress_gain = random.uniform(5, 20)
        new_progress = min(100, project["progress"] + progress_gain)
        new_days = project["days_elapsed"] + 1
        budget_spent = project["budget_spent"] + random.uniform(1, 5)

        status = "active" if new_progress < 100 else "completed"
        if new_days > project["timeline_days"] and new_progress < 80:
            status = "failed"

        await db.update_project(
            project_id,
            progress=round(new_progress, 1),
            days_elapsed=new_days,
            budget_spent=round(budget_spent, 2),
            status=status,
        )

        if status == "completed":
            self.stats["projects_completed"] += 1
            actual_impact = project["expected_impact"] * random.uniform(0.5, 1.5)
            await db.update_project(project_id, actual_impact=round(actual_impact, 1))
        elif status == "failed":
            self.stats["projects_failed"] += 1

        return {
            "success": True, "progress": round(new_progress, 1),
            "status": status, "days_elapsed": new_days,
        }

    async def get_project(self, project_id: str) -> dict | None:
        return await db.get_project(project_id)

    async def list_projects(self, organization_id: str | None = None,
                            status: str | None = None, limit: int = 50) -> list[dict]:
        return await db.list_projects(organization_id, status, limit=limit)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


project_manager = ProjectManager()
