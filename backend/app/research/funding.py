import json
import logging
import random
from datetime import datetime, timezone

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.funding")

FUNDING_SOURCES = {
    "government": {"amount_range": (50, 500), "risk_tolerance": 0.3, "approval_rate": 0.4},
    "company": {"amount_range": (100, 1000), "risk_tolerance": 0.5, "approval_rate": 0.5},
    "private_investor": {"amount_range": (20, 200), "risk_tolerance": 0.7, "approval_rate": 0.3},
    "foundation": {"amount_range": (30, 300), "risk_tolerance": 0.4, "approval_rate": 0.45},
}


class FundingEngine:
    def __init__(self):
        self.stats = {
            "funding_requests": 0,
            "funding_granted": 0,
            "total_funded": 0,
            "total_disbursed": 0,
        }

    async def request_funding(self, project_id: str, source_type: str,
                              funder_organization: str | None = None,
                              amount: float | None = None,
                              funder_agent_id: str | None = None) -> dict:
        config = FUNDING_SOURCES.get(source_type, FUNDING_SOURCES["government"])
        if not amount:
            amount = random.uniform(*config["amount_range"])

        proposal_score = random.uniform(0.3, 0.9)
        risk_assessment = random.uniform(0.1, 0.8)
        approved = random.random() < config["approval_rate"]

        status = "approved" if approved else "rejected"
        disbursed = amount if approved else 0

        funding_id = await db.create_funding(
            project_id=project_id,
            funder_agent_id=funder_agent_id,
            funder_organization=funder_organization,
            funding_source_type=source_type,
            amount=amount,
            disbursed=disbursed,
            status=status,
            proposal_score=round(proposal_score, 3),
            risk_assessment=round(risk_assessment, 3),
        )
        self.stats["funding_requests"] += 1

        if approved:
            self.stats["funding_granted"] += 1
            self.stats["total_funded"] += amount
            self.stats["total_disbursed"] += disbursed

            project = await db.get_project(project_id)
            if project:
                new_budget = project["budget"] + amount
                await db.update_project(project_id, budget=new_budget, funding_source=source_type)

        await dispatch(Event(EventType.FUNDING_GRANTED, {
            "funding_id": funding_id, "project_id": project_id,
            "source_type": source_type, "amount": amount,
            "status": status,
        }))

        return {
            "funding_id": funding_id, "amount": amount,
            "status": status, "source_type": source_type,
            "proposal_score": round(proposal_score, 3),
        }

    async def list_funding(self, project_id: str | None = None,
                           status: str | None = None) -> list[dict]:
        return await db.list_funding(project_id, status)

    async def get_funding_stats(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "sources": {k: v["amount_range"] for k, v in FUNDING_SOURCES.items()},
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


funding_engine = FundingEngine()
