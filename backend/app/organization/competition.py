from __future__ import annotations

import logging
import random

from app.organization import persistence as op

logger = logging.getLogger("nexus.organization.competition")


class CompanyCompetition:
    async def compete(self, company_a_id: str, company_b_id: str, domain: str = "market") -> dict:
        company_a = await op.get_company(company_a_id)
        company_b = await op.get_company(company_b_id)
        if not company_a or not company_b:
            return {"error": "One or both companies not found"}

        score_a = self._calculate_competitive_score(company_a)
        score_b = self._calculate_competitive_score(company_b)
        total = score_a + score_b
        share_a = round(score_a / max(total, 1) * 100, 1)
        share_b = round(score_b / max(total, 1) * 100, 1)

        winner_id = company_a_id if score_a > score_b else company_b_id
        loser_id = company_b_id if score_a > score_a else company_a_id

        await op.add_memory(
            company_a_id, "competition",
            f"Competed against {company_b['name']}",
            f"Domain: {domain}, Market share: {share_a}%",
            "medium",
        )
        await op.add_memory(
            company_b_id, "competition",
            f"Competed against {company_a['name']}",
            f"Domain: {domain}, Market share: {share_b}%",
            "medium",
        )

        return {
            "domain": domain,
            "company_a": {"id": company_a_id, "name": company_a["name"], "score": score_a, "share": share_a},
            "company_b": {"id": company_b_id, "name": company_b["name"], "score": score_b, "share": share_b},
            "winner_id": winner_id,
        }

    async def form_partnership(self, company_a_id: str, company_b_id: str, terms: str = "") -> dict:
        company_a = await op.get_company(company_a_id)
        company_b = await op.get_company(company_b_id)
        if not company_a or not company_b:
            return {"error": "One or both companies not found"}

        partnership = {
            "company_a": company_a_id,
            "company_b": company_b_id,
            "status": "active",
            "terms": terms or "General partnership",
        }

        await op.add_memory(
            company_a_id, "partnership_formed",
            f"Partnership with {company_b['name']}",
            terms or "General partnership", "high",
        )
        await op.add_memory(
            company_b_id, "partnership_formed",
            f"Partnership with {company_a['name']}",
            terms or "General partnership", "high",
        )

        return partnership

    async def attempt_acquisition(self, acquirer_id: str, target_id: str, offer_amount: float) -> dict:
        acquirer = await op.get_company(acquirer_id)
        target = await op.get_company(target_id)
        if not acquirer or not target:
            return {"error": "One or both companies not found"}

        if acquirer["treasury_balance"] < offer_amount:
            return {"error": "Insufficient funds for acquisition"}

        fair_value = target["revenue"] * 3 + target["treasury_balance"] + target["reputation"] * 10
        acceptance_threshold = fair_value * 0.8

        accepted = offer_amount >= acceptance_threshold
        if accepted:
            await op.update_company(target_id, status="acquired", owner_id=acquirer["owner_id"])
            await op.add_memory(
                acquirer_id, "acquisition_completed",
                f"Acquired {target['name']}",
                f"Offer: {offer_amount:.0f} NXC", "high",
            )
            return {
                "accepted": True,
                "offer": offer_amount,
                "fair_value": round(fair_value, 2),
                "target_name": target["name"],
            }
        else:
            return {
                "accepted": False,
                "offer": offer_amount,
                "fair_value": round(fair_value, 2),
                "minimum_required": round(acceptance_threshold, 2),
                "target_name": target["name"],
            }

    async def merge_companies(self, company_a_id: str, company_b_id: str) -> dict:
        company_a = await op.get_company(company_a_id)
        company_b = await op.get_company(company_b_id)
        if not company_a or not company_b:
            return {"error": "One or both companies not found"}

        new_treasury = company_a["treasury_balance"] + company_b["treasury_balance"]
        new_revenue = company_a["revenue"] + company_b["revenue"]
        new_employees = company_a["employee_count"] + company_b["employee_count"]
        new_reputation = (company_a["reputation"] + company_b["reputation"]) / 2

        await op.update_company(
            company_a_id,
            treasury_balance=new_treasury, revenue=new_revenue,
            employee_count=new_employees, reputation=new_reputation,
            name=f"{company_a['name']} + {company_b['name']}",
        )
        await op.update_company(company_b_id, status="merged")

        await op.add_memory(
            company_a_id, "merger_completed",
            f"Merged with {company_b['name']}",
            f"New employee count: {new_employees}", "high",
        )

        return {
            "merged_company": company_a_id,
            "absorbed_company": company_b_id,
            "new_treasury": round(new_treasury, 2),
            "new_revenue": round(new_revenue, 2),
            "new_employees": new_employees,
        }

    def _calculate_competitive_score(self, company: dict) -> float:
        revenue_score = min(company.get("revenue", 0) / 1000, 1.0) * 0.3
        reputation_score = company.get("reputation", 50) / 100 * 0.25
        employee_score = min(company.get("employee_count", 0) / 50, 1.0) * 0.2
        balance_score = min(company.get("treasury_balance", 0) / 500, 1.0) * 0.15
        project_score = min(company.get("successful_projects", 0) / 10, 1.0) * 0.1
        return round(revenue_score + reputation_score + employee_score + balance_score + project_score, 3)


competition = CompanyCompetition()
