from __future__ import annotations

import logging
import random

from app.organization import persistence as op

logger = logging.getLogger("nexus.organization.strategy")

STRATEGY_TEMPLATES = {
    "growth": [
        {"title": "Expand market reach", "goal": "Increase market share by 10%", "timeline": 60, "resources": {"budget": 200, "employees": 3}},
        {"title": "Launch new product", "goal": "Develop and launch a new product line", "timeline": 90, "resources": {"budget": 500, "employees": 5}},
        {"title": "Hire key talent", "goal": "Recruit 5 senior engineers", "timeline": 30, "resources": {"budget": 100, "employees": 1}},
    ],
    "cost_reduction": [
        {"title": "Optimize operations", "goal": "Reduce operational costs by 15%", "timeline": 45, "resources": {"budget": 50, "employees": 2}},
        {"title": "Automate processes", "goal": "Automate 3 manual workflows", "timeline": 60, "resources": {"budget": 100, "employees": 2}},
    ],
    "innovation": [
        {"title": "R&D initiative", "goal": "Develop prototype for new technology", "timeline": 90, "resources": {"budget": 300, "employees": 4}},
        {"title": "Research partnership", "goal": "Establish collaboration with research lab", "timeline": 45, "resources": {"budget": 50, "employees": 1}},
    ],
    "market_penetration": [
        {"title": "Customer acquisition", "goal": "Acquire 100 new customers", "timeline": 30, "resources": {"budget": 150, "employees": 2}},
        {"title": "Brand awareness", "goal": "Increase brand visibility by 25%", "timeline": 45, "resources": {"budget": 100, "employees": 1}},
    ],
    "diversification": [
        {"title": "Enter new market", "goal": "Establish presence in adjacent market", "timeline": 120, "resources": {"budget": 400, "employees": 4}},
        {"title": "Acquire competitor", "goal": "Acquire smaller competitor", "timeline": 90, "resources": {"budget": 1000, "employees": 2}},
    ],
}


class StrategyEngine:
    async def create_strategy(
        self, company_id: str, strategy_type: str = "growth",
        title: str = "", goal: str = "", timeline_days: int = 30,
    ) -> dict:
        if not title or not goal:
            templates = STRATEGY_TEMPLATES.get(strategy_type, STRATEGY_TEMPLATES["growth"])
            template = random.choice(templates)
            title = title or template["title"]
            goal = goal or template["goal"]
            timeline_days = timeline_days or template["timeline"]

        strategy = await op.create_strategy(
            company_id=company_id, title=title, goal=goal,
            strategy_type=strategy_type, timeline_days=timeline_days,
            expected_outcome=f"Achieve: {goal}",
        )
        await op.add_memory(
            company_id, "strategy_created",
            f"New strategy: {title}",
            f"Type: {strategy_type}, Goal: {goal}",
            "high",
        )
        logger.info("strategy_created company=%s type=%s title=%s", company_id, strategy_type, title)
        return strategy

    async def auto_generate_strategy(self, company_id: str) -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}

        if company["treasury_balance"] < 100:
            strategy_type = "cost_reduction"
        elif company["reputation"] > 70:
            strategy_type = random.choice(["growth", "innovation", "diversification"])
        elif company["employee_count"] < 5:
            strategy_type = "growth"
        else:
            strategy_type = random.choice(["growth", "market_penetration", "innovation"])

        return await self.create_strategy(company_id, strategy_type)

    async def advance_strategy(self, strategy_id: str) -> dict:
        strategy = await op.get_strategies("")
        s = next((s for s in strategy if s["id"] == strategy_id), None)
        if not s:
            return {"error": "Strategy not found"}

        progress_increment = random.uniform(5, 20)
        new_progress = min(s["progress"] + progress_increment, 100)
        status = "completed" if new_progress >= 100 else "in_progress" if new_progress > 0 else "active"

        result = await op.update_strategy(strategy_id, progress=new_progress, status=status)
        if status == "completed":
            await op.add_memory(
                s["company_id"], "strategy_completed",
                f"Strategy completed: {s['title']}",
                f"Progress: {new_progress:.0f}%",
                "high",
            )
        return result or s

    async def evaluate_strategy(self, strategy_id: str) -> dict:
        strategies = await op.get_strategies("")
        s = next((s for s in strategies if s["id"] == strategy_id), None)
        if not s:
            return {"error": "Strategy not found"}

        effectiveness = s["progress"] / max(s["timeline_days"], 1) * 10
        on_track = s["progress"] >= (s["timeline_days"] * 0.5)
        return {
            "strategy_id": strategy_id,
            "title": s["title"],
            "progress": s["progress"],
            "effectiveness": round(min(effectiveness, 100), 1),
            "on_track": on_track,
            "status": s["status"],
            "days_remaining": max(s["timeline_days"] - int(s["progress"] * s["timeline_days"] / 100), 0),
        }

    async def get_company_strategies(self, company_id: str) -> dict:
        strategies = await op.get_strategies(company_id)
        active = [s for s in strategies if s["status"] in ("active", "in_progress")]
        completed = [s for s in strategies if s["status"] == "completed"]
        return {
            "total": len(strategies),
            "active": len(active),
            "completed": len(completed),
            "strategies": strategies,
        }


strategy_engine = StrategyEngine()
