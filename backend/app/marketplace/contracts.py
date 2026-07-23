from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.marketplace import persistence as mp

logger = logging.getLogger("nexus.marketplace.contracts")


class ContractManager:
    async def create_contract(
        self, task_id: str, proposal_id: str, poster_id: str,
        agent_id: str, agreed_reward: float, terms: str = "",
    ) -> dict:
        contract = await mp.create_contract(
            task_id=task_id, proposal_id=proposal_id, poster_id=poster_id,
            agent_id=agent_id, agreed_reward=agreed_reward, terms=terms,
        )
        await mp.update_task(task_id, status="in_progress")
        logger.info("contract_created contract=%s task=%s agent=%s", contract["id"], task_id, agent_id)
        return contract

    async def accept_contract(self, contract_id: str) -> dict:
        contract = await mp.get_contract(contract_id)
        if not contract or contract["status"] != "created":
            return {"error": "Contract not found or not in created status"}
        updated = await mp.update_contract(
            contract_id, status="accepted",
            accepted_at=datetime.now(timezone.utc),
        )
        logger.info("contract_accepted contract=%s", contract_id)
        return updated

    async def start_contract(self, contract_id: str) -> dict:
        contract = await mp.get_contract(contract_id)
        if not contract or contract["status"] != "accepted":
            return {"error": "Contract not found or not accepted"}
        updated = await mp.update_contract(
            contract_id, status="active",
            started_at=datetime.now(timezone.utc),
        )
        logger.info("contract_started contract=%s", contract_id)
        return updated

    async def complete_contract(self, contract_id: str, result: str = "", rating: float = 5.0, feedback: str = "") -> dict:
        contract = await mp.get_contract(contract_id)
        if not contract or contract["status"] != "active":
            return {"error": "Contract not found or not active"}
        updated = await mp.update_contract(
            contract_id, status="completed", result=result,
            rating=rating, feedback=feedback,
            completed_at=datetime.now(timezone.utc),
        )
        await mp.update_task(contract["task_id"], status="completed", result=result)
        logger.info("contract_completed contract=%s rating=%.1f", contract_id, rating)
        return updated

    async def fail_contract(self, contract_id: str, reason: str = "") -> dict:
        contract = await mp.get_contract(contract_id)
        if not contract:
            return {"error": "Contract not found"}
        updated = await mp.update_contract(
            contract_id, status="failed", result=reason,
            failed_at=datetime.now(timezone.utc),
        )
        await mp.update_task(contract["task_id"], status="open")
        logger.info("contract_failed contract=%s reason=%s", contract_id, reason)
        return updated

    async def cancel_contract(self, contract_id: str) -> dict:
        contract = await mp.get_contract(contract_id)
        if not contract:
            return {"error": "Contract not found"}
        updated = await mp.update_contract(contract_id, status="cancelled")
        await mp.update_task(contract["task_id"], status="open")
        logger.info("contract_cancelled contract=%s", contract_id)
        return updated

    async def get_contract(self, contract_id: str) -> dict | None:
        return await mp.get_contract(contract_id)

    async def list_agent_contracts(self, agent_id: str, status: str = "") -> list[dict]:
        return await mp.list_contracts_by_agent(agent_id, status=status)

    async def list_poster_contracts(self, poster_id: str, status: str = "") -> list[dict]:
        return await mp.list_contracts_by_poster(poster_id, status=status)

    async def get_contract_stats(self, agent_id: str) -> dict:
        all_contracts = await mp.list_contracts_by_agent(agent_id)
        completed = [c for c in all_contracts if c["status"] == "completed"]
        failed = [c for c in all_contracts if c["status"] == "failed"]
        ratings = [c["rating"] for c in completed if c.get("rating") is not None]
        return {
            "total": len(all_contracts),
            "completed": len(completed),
            "failed": len(failed),
            "active": len([c for c in all_contracts if c["status"] in ("created", "accepted", "active")]),
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "success_rate": round(len(completed) / max(len(all_contracts), 1) * 100, 1),
            "total_earned": round(sum(c["agreed_reward"] for c in completed), 2),
        }


contract_manager = ContractManager()
