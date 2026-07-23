from __future__ import annotations

import logging
import random
from typing import Any

from app.marketplace import persistence as mp

logger = logging.getLogger("nexus.marketplace.task_manager")

TASK_CATEGORIES = {
    "technology": ["Build API integration", "Deploy microservice", "Security audit", "Code review", "Database optimization"],
    "analytics": ["Data pipeline setup", "ML model training", "Dashboard creation", "A/B test analysis", "ETL workflow"],
    "finance": ["Portfolio rebalance", "Risk assessment", "Budget forecast", "Tax optimization", "Audit preparation"],
    "marketing": ["Campaign strategy", "SEO optimization", "Content calendar", "Social media plan", "Brand refresh"],
    "legal": ["Contract review", "Compliance check", "IP filing", "Regulatory analysis", "Policy draft"],
    "design": ["UI redesign", "Wireframe set", "Brand identity", "Accessibility audit", "Prototype build"],
    "creative": ["Video production", "Copywriting", "Illustration series", "Podcast editing", "Motion graphics"],
    "science": ["Research paper", "Lab protocol", "Data collection", "Experiment design", "Literature review"],
    "logistics": ["Supply chain audit", "Route optimization", "Inventory system", "Vendor negotiation", "Warehouse layout"],
    "healthcare": ["Patient intake system", "Compliance report", "Telehealth setup", "EHR migration", "Training module"],
}

PRIORITY_WEIGHTS = {"low": 1, "medium": 2, "high": 3, "urgent": 5}


class TaskManager:
    async def create_task(
        self, poster_id: str, title: str, description: str = "",
        required_skills: list[str] | None = None, reward: float = 0,
        priority: str = "medium", deadline: str | None = None,
    ) -> dict:
        from datetime import datetime, timezone
        dl = None
        if deadline:
            try:
                dl = datetime.fromisoformat(deadline.replace("Z", "+00:00"))
            except ValueError:
                pass
        task = await mp.create_task(
            posted_by=poster_id, title=title, description=description,
            required_skills=required_skills or [], reward=reward,
            priority=priority, deadline=dl,
        )
        logger.info("task_created task=%s title=%s reward=%.0f", task["id"], title, reward)
        return task

    async def get_task(self, task_id: str) -> dict | None:
        return await mp.get_task(task_id)

    async def list_tasks(self, status: str = "", priority: str = "", skip: int = 0, limit: int = 50) -> list[dict]:
        return await mp.list_tasks(status=status, priority=priority, skip=skip, limit=limit)

    async def search_tasks(self, query: str = "", skills: list[str] | None = None, min_reward: float = 0) -> list[dict]:
        return await mp.search_tasks(query=query, skills=skills, min_reward=min_reward)

    async def assign_agent(self, task_id: str, agent_id: str) -> dict | None:
        task = await mp.get_task(task_id)
        if not task:
            return None
        if task["status"] != "open":
            return None
        updated = await mp.update_task(task_id, status="in_progress")
        if updated:
            logger.info("task_assigned task=%s agent=%s", task_id, agent_id)
        return updated

    async def complete_task(self, task_id: str, result: str = "") -> dict | None:
        task = await mp.get_task(task_id)
        if not task:
            return None
        updated = await mp.update_task(task_id, status="completed", result=result)
        if updated:
            logger.info("task_completed task=%s", task_id)
        return updated

    async def generate_marketplace_tasks(self, count: int = 5) -> list[dict]:
        categories = list(TASK_CATEGORIES.keys())
        skills_pool = [
            "Python", "JavaScript", "Machine Learning", "Data Analysis", "UI/UX",
            "Contract Law", "SEO", "Financial Modeling", "System Design", "Writing",
            "AutoCAD", "Pen Testing", "Statistics", "Negotiation", "GIS",
        ]
        created = []
        for _ in range(count):
            cat = random.choice(categories)
            title = random.choice(TASK_CATEGORIES[cat])
            reward = round(random.uniform(10, 200), 2)
            priority = random.choice(["low", "medium", "high"])
            skills = random.sample(skills_pool, k=random.randint(1, 3))
            task = await self.create_task(
                poster_id="marketplace",
                title=title,
                description=f"Automated marketplace task in {cat} category",
                required_skills=skills,
                reward=reward,
                priority=priority,
            )
            created.append(task)
        return created

    async def get_stats(self) -> dict:
        return await mp.get_marketplace_stats()


task_manager = TaskManager()
