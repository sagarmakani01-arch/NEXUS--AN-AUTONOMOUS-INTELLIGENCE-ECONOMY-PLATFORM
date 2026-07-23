from __future__ import annotations

import asyncio
import json
import logging
import random
from datetime import datetime, timezone

from app.organization import persistence as op
from app.organization.competition import competition
from app.organization.finance import finance_manager
from app.organization.hiring import hiring_engine
from app.organization.orgchart import org_chart
from app.organization.strategy import strategy_engine

logger = logging.getLogger("nexus.organization.engine")


class CompanyEngine:
    def __init__(self) -> None:
        self._running = False
        self._task: asyncio.Task | None = None
        self._tick_interval = 60.0
        self._active_companies: dict[str, dict] = {}

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("company_engine_started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("company_engine_stopped")

    async def _run_loop(self) -> None:
        try:
            while self._running:
                await self._tick()
                await asyncio.sleep(self._tick_interval)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("company_engine_loop_error: %s", exc)

    async def _tick(self) -> None:
        try:
            await self._process_companies()
        except Exception as exc:
            logger.error("company_tick_error: %s", exc)

    async def _process_companies(self) -> None:
        companies = await op.list_companies()
        for company in companies:
            cid = company["id"]
            if cid not in self._active_companies:
                self._active_companies[cid] = {"last_tick": datetime.now(timezone.utc)}

            if company["status"] == "startup" and company["employee_count"] >= 3:
                await op.update_company(cid, status="growing")
                await op.add_memory(cid, "status_change", "Company grew to growing stage", "", "high")

            if company["status"] == "growing" and company["revenue"] > 500:
                await op.update_company(cid, status="stable")
                await op.add_memory(cid, "status_change", "Company reached stable stage", "", "high")

            if company["treasury_balance"] < 0 and company["status"] != "bankrupt":
                await op.update_company(cid, status="bankrupt")
                await op.add_memory(cid, "company_failed", "Company went bankrupt", "", "high")

            company_age = company.get("company_age", 0) + 1
            await op.update_company(cid, company_age=company_age)

    async def create_company(
        self, owner_id: str, name: str, description: str = "",
        industry: str = "technology", mission: str = "", vision: str = "",
        founder_agent_id: str | None = None, initial_capital: float = 500,
    ) -> dict:
        company = await op.create_company(
            owner_id=owner_id, name=name, description=description,
            industry=industry, mission=mission, vision=vision,
            founder_agent_id=founder_agent_id, treasury_balance=initial_capital,
        )
        await finance_manager.deposit(company["id"], initial_capital, "investment", "Initial capital")
        await org_chart.initialize_departments(company["id"], industry)
        await op.add_memory(company["id"], "company_founded", f"Founded: {name}", f"Industry: {industry}", "high")

        if founder_agent_id:
            await hiring_engine.hire_agent(
                company["id"], founder_agent_id,
                role="c_level", department="executive", title="Founder & CEO",
            )

        self._active_companies[company["id"]] = {"created": datetime.now(timezone.utc)}
        logger.info("company_created company=%s name=%s industry=%s", company["id"], name, industry)
        return company

    async def get_company_profile(self, company_id: str) -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}

        members = await op.get_members(company_id)
        strategies = await op.get_strategies(company_id)
        finances = await op.get_finances(company_id, limit=20)
        memories = await op.get_memories(company_id, limit=20)
        health = await finance_manager.get_company_health(company_id)
        org = await org_chart.get_org_chart(company_id)
        fin_report = await finance_manager.get_financial_report(company_id)

        return {
            "company": company,
            "organization": org,
            "strategies": strategies,
            "recent_finances": finances,
            "recent_memories": memories,
            "health": health,
            "financial_report": fin_report,
            "member_count": len(members),
        }

    async def list_companies(self, status: str = "", industry: str = "") -> list[dict]:
        return await op.list_companies(status=status, industry=industry)

    async def hire_agent(self, company_id: str, agent_id: str, role: str = "employee", department: str = "", title: str = "", salary: float = 0) -> dict:
        return await hiring_engine.hire_agent(company_id, agent_id, role, department, title, salary)

    async def fire_agent(self, company_id: str, agent_id: str, reason: str = "") -> dict:
        return await hiring_engine.fire_agent(company_id, agent_id, reason)

    async def promote_agent(self, company_id: str, agent_id: str, new_role: str, new_title: str = "") -> dict:
        return await hiring_engine.promote_agent(company_id, agent_id, new_role, new_title)

    async def deposit(self, company_id: str, amount: float, category: str = "investment") -> dict:
        return await finance_manager.deposit(company_id, amount, category)

    async def withdraw(self, company_id: str, amount: float, category: str = "expense") -> dict:
        return await finance_manager.withdraw(company_id, amount, category)

    async def generate_revenue(self, company_id: str, amount: float, source: str = "product") -> dict:
        return await finance_manager.generate_revenue(company_id, amount, source)

    async def create_strategy(self, company_id: str, strategy_type: str = "growth", title: str = "", goal: str = "") -> dict:
        return await strategy_engine.create_strategy(company_id, strategy_type, title, goal)

    async def compete(self, company_a_id: str, company_b_id: str, domain: str = "market") -> dict:
        return await competition.compete(company_a_id, company_b_id, domain)

    async def form_partnership(self, company_a_id: str, company_b_id: str, terms: str = "") -> dict:
        return await competition.form_partnership(company_a_id, company_b_id, terms)

    async def acquire(self, acquirer_id: str, target_id: str, offer: float) -> dict:
        return await competition.attempt_acquisition(acquirer_id, target_id, offer)

    async def merge(self, company_a_id: str, company_b_id: str) -> dict:
        return await competition.merge_companies(company_a_id, company_b_id)

    async def get_stats(self) -> dict:
        return await op.get_company_stats()

    def get_state(self) -> dict:
        return {
            "running": self._running,
            "active_companies": len(self._active_companies),
        }


company_engine = CompanyEngine()
