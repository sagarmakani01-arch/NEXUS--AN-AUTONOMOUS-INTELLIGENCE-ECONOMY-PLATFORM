from __future__ import annotations

import json
import logging
import random
from typing import Any

from app.execution import persistence as ep

logger = logging.getLogger("nexus.execution.goal_decomposition")

GOAL_TEMPLATES = {
    "technology": {
        "Build an e-commerce website": [
            {"title": "Analyze requirements", "skills": ["System Design", "Writing"], "duration": 2, "cost": 5},
            {"title": "Design database schema", "skills": ["Database Design", "System Design"], "duration": 3, "cost": 8},
            {"title": "Build backend API", "skills": ["Python", "API Development"], "duration": 8, "cost": 20},
            {"title": "Create frontend UI", "skills": ["React", "UI/UX"], "duration": 6, "cost": 15},
            {"title": "Implement payment system", "skills": ["Python", "Security"], "duration": 4, "cost": 12},
            {"title": "Write tests", "skills": ["Testing", "Python"], "duration": 4, "cost": 10},
            {"title": "Deploy to production", "skills": ["DevOps", "System Design"], "duration": 2, "cost": 8},
        ],
        "Build a data pipeline": [
            {"title": "Define data sources", "skills": ["Data Analysis", "Statistics"], "duration": 2, "cost": 5},
            {"title": "Design ETL workflow", "skills": ["Python", "Data Analysis"], "duration": 3, "cost": 8},
            {"title": "Implement extraction", "skills": ["Python", "API Development"], "duration": 4, "cost": 12},
            {"title": "Build transformation layer", "skills": ["Python", "Machine Learning"], "duration": 5, "cost": 15},
            {"title": "Create loading mechanism", "skills": ["Database Design", "Python"], "duration": 3, "cost": 10},
            {"title": "Set up monitoring", "skills": ["DevOps", "Data Analysis"], "duration": 2, "cost": 6},
        ],
        "Develop a mobile app": [
            {"title": "Create wireframes", "skills": ["UI/UX", "Design"], "duration": 2, "cost": 5},
            {"title": "Build core features", "skills": ["React", "JavaScript"], "duration": 8, "cost": 20},
            {"title": "Implement authentication", "skills": ["Security", "API Development"], "duration": 3, "cost": 10},
            {"title": "Add push notifications", "skills": ["React", "API Development"], "duration": 2, "cost": 6},
            {"title": "Performance optimization", "skills": ["System Design", "Testing"], "duration": 3, "cost": 8},
            {"title": "App store submission", "skills": ["DevOps", "Writing"], "duration": 1, "cost": 3},
        ],
    },
    "analytics": {
        "Build a recommendation engine": [
            {"title": "Collect user data", "skills": ["Data Analysis", "Python"], "duration": 3, "cost": 8},
            {"title": "Feature engineering", "skills": ["Machine Learning", "Statistics"], "duration": 4, "cost": 12},
            {"title": "Train model", "skills": ["Machine Learning", "Python"], "duration": 5, "cost": 15},
            {"title": "Evaluate performance", "skills": ["Statistics", "Machine Learning"], "duration": 2, "cost": 6},
            {"title": "Deploy model", "skills": ["DevOps", "Python"], "duration": 2, "cost": 8},
        ],
        "Create analytics dashboard": [
            {"title": "Define metrics", "skills": ["Data Analysis", "Statistics"], "duration": 2, "cost": 5},
            {"title": "Design visualizations", "skills": ["UI/UX", "Data Analysis"], "duration": 3, "cost": 8},
            {"title": "Build data connectors", "skills": ["Python", "API Development"], "duration": 4, "cost": 12},
            {"title": "Implement dashboard", "skills": ["React", "Data Analysis"], "duration": 5, "cost": 15},
            {"title": "Add real-time updates", "skills": ["System Design", "React"], "duration": 2, "cost": 6},
        ],
    },
    "finance": {
        "Build a trading bot": [
            {"title": "Research market data", "skills": ["Quantitative Analysis", "Data Analysis"], "duration": 3, "cost": 8},
            {"title": "Design strategy", "skills": ["Quantitative Analysis", "Risk Assessment"], "duration": 4, "cost": 12},
            {"title": "Implement backtesting", "skills": ["Python", "Statistics"], "duration": 5, "cost": 15},
            {"title": "Build execution engine", "skills": ["Python", "API Development"], "duration": 4, "cost": 12},
            {"title": "Risk management", "skills": ["Risk Assessment", "Quantitative Analysis"], "duration": 3, "cost": 8},
        ],
        "Create financial model": [
            {"title": "Gather historical data", "skills": ["Data Analysis", "Excel"], "duration": 2, "cost": 5},
            {"title": "Build model framework", "skills": ["Quantitative Analysis", "Python"], "duration": 4, "cost": 12},
            {"title": "Calibrate parameters", "skills": ["Statistics", "Quantitative Analysis"], "duration": 3, "cost": 8},
            {"title": "Validate results", "skills": ["Risk Assessment", "Statistics"], "duration": 2, "cost": 6},
        ],
    },
    "creative": {
        "Produce a marketing campaign": [
            {"title": "Market research", "skills": ["Data Analysis", "Writing"], "duration": 2, "cost": 5},
            {"title": "Create content strategy", "skills": ["Content Strategy", "Writing"], "duration": 3, "cost": 8},
            {"title": "Design visual assets", "skills": ["UI/UX", "Illustration"], "duration": 4, "cost": 12},
            {"title": "Write copy", "skills": ["Writing", "Content Strategy"], "duration": 3, "cost": 8},
            {"title": "Launch campaign", "skills": ["SEO", "Analytics"], "duration": 2, "cost": 6},
        ],
        "Build a content platform": [
            {"title": "Define content types", "skills": ["System Design", "Writing"], "duration": 2, "cost": 5},
            {"title": "Build CMS backend", "skills": ["Python", "API Development"], "duration": 5, "cost": 15},
            {"title": "Create editor UI", "skills": ["React", "UI/UX"], "duration": 4, "cost": 12},
            {"title": "Implement search", "skills": ["System Design", "Python"], "duration": 3, "cost": 8},
            {"title": "Add analytics", "skills": ["Data Analysis", "React"], "duration": 2, "cost": 6},
        ],
    },
    "science": {
        "Conduct a research study": [
            {"title": "Literature review", "skills": ["Research", "Writing"], "duration": 4, "cost": 10},
            {"title": "Design methodology", "skills": ["Research", "Statistics"], "duration": 3, "cost": 8},
            {"title": "Collect data", "skills": ["Data Analysis", "Research"], "duration": 5, "cost": 15},
            {"title": "Analyze results", "skills": ["Statistics", "Machine Learning"], "duration": 4, "cost": 12},
            {"title": "Write paper", "skills": ["Writing", "Research"], "duration": 5, "cost": 15},
        ],
    },
}

SKILL_POOL = [
    "Python", "JavaScript", "React", "Machine Learning", "Data Analysis",
    "UI/UX", "System Design", "API Development", "Database Design", "Security",
    "DevOps", "Testing", "Writing", "Statistics", "Risk Assessment",
    "Quantitative Analysis", "Content Strategy", "SEO", "Analytics",
    "Illustration", "Design", "Research", "Excel", "Thermodynamics",
    "CAD", "Pen Testing", "GIS", "Negotiation",
]


class GoalDecompositionEngine:
    async def decompose_goal(
        self, project_id: str, goal: str, agent_skills: list[str] | None = None,
    ) -> list[dict]:
        tasks = self._match_template(goal)
        if not tasks:
            tasks = self._generate_generic_tasks(goal, agent_skills)

        created_tasks = []
        for i, task_def in enumerate(tasks):
            deps = [created_tasks[i - 1]["id"]] if i > 0 and created_tasks else []
            task = await ep.create_execution_task(
                project_id=project_id,
                title=task_def["title"],
                description=f"Part of: {goal}",
                required_skills=task_def.get("skills", []),
                priority=task_def.get("priority", "medium"),
                dependencies=deps,
                estimated_cost=task_def.get("cost", 10),
                estimated_duration=task_def.get("duration", 4),
            )
            created_tasks.append(task)

        await ep.update_project(project_id, total_tasks=len(created_tasks))
        logger.info("goal_decomposed project=%s goal=%s tasks=%d", project_id, goal, len(created_tasks))
        return created_tasks

    def _match_template(self, goal: str) -> list[dict] | None:
        goal_lower = goal.lower()
        for category_templates in GOAL_TEMPLATES.values():
            for template_goal, tasks in category_templates.items():
                if template_goal.lower() in goal_lower or goal_lower in template_goal.lower():
                    return [dict(t) for t in tasks]
        for category_templates in GOAL_TEMPLATES.values():
            for template_goal, tasks in category_templates.items():
                template_words = set(template_goal.lower().split())
                goal_words = set(goal_lower.split())
                overlap = len(template_words & goal_words)
                if overlap >= 2:
                    return [dict(t) for t in tasks]
        return None

    def _generate_generic_tasks(self, goal: str, agent_skills: list[str] | None = None) -> list[dict]:
        phases = [
            ("Research and analysis", ["Research", "Data Analysis"], 3, 8),
            ("Design and planning", ["System Design", "Writing"], 2, 6),
            ("Core implementation", agent_skills[:2] if agent_skills else ["Python"], 6, 18),
            ("Testing and validation", ["Testing", "Data Analysis"], 3, 10),
            ("Deployment and delivery", ["DevOps", "System Design"], 2, 6),
        ]
        tasks = []
        for title, skills, duration, cost in phases:
            actual_skills = [s for s in skills if s in SKILL_POOL] or random.sample(SKILL_POOL, 2)
            tasks.append({
                "title": f"{title} for: {goal}",
                "skills": actual_skills,
                "duration": duration,
                "cost": cost,
                "priority": "high" if "implementation" in title.lower() else "medium",
            })
        return tasks

    async def get_task_dependencies(self, project_id: str) -> dict[str, list[str]]:
        tasks = await ep.list_execution_tasks(project_id=project_id)
        deps = {}
        for task in tasks:
            deps[task["id"]] = task.get("dependencies", [])
        return deps

    async def get_ready_tasks(self, project_id: str) -> list[dict]:
        tasks = await ep.list_execution_tasks(project_id=project_id, status="created")
        deps = await self.get_task_dependencies(project_id)
        completed = set()
        for t in await ep.list_execution_tasks(project_id=project_id, status="completed"):
            completed.add(t["id"])
        ready = []
        for task in tasks:
            task_deps = deps.get(task["id"], [])
            if all(d in completed for d in task_deps):
                ready.append(task)
        return ready

    async def estimate_project_cost(self, project_id: str) -> dict:
        tasks = await ep.list_execution_tasks(project_id=project_id)
        total_estimated = sum(t.get("estimated_cost", 0) for t in tasks)
        total_duration = sum(t.get("estimated_duration", 0) for t in tasks)
        unique_skills = set()
        for t in tasks:
            unique_skills.update(t.get("required_skills", []))
        return {
            "total_estimated_cost": total_estimated,
            "total_estimated_duration": total_duration,
            "task_count": len(tasks),
            "required_skills": list(unique_skills),
        }


goal_decomposition = GoalDecompositionEngine()
