from __future__ import annotations
import logging
from app.resources import persistence

logger = logging.getLogger("nexus.resources.compute")

COMPUTE_COSTS = {
    "simple_decision": 1,
    "contract_offer": 2,
    "company_invitation": 3,
    "negotiation": 3,
    "skill_selection": 2,
    "investment_opportunity": 4,
    "emergency": 2,
    "hiring": 4,
    "promotion": 3,
    "company_creation": 8,
    "goal_selection": 2,
    "task_acceptance": 1,
    "complex_planning": 8,
    "long_term_strategy": 20,
}

class ComputeManager:
    async def get_balance(self, agent_id: str) -> dict:
        wallet = await persistence.get_or_create_wallet(agent_id)
        return {
            "agent_id": agent_id,
            "compute_credits": wallet.get("compute_credits", 0),
            "compute_used": wallet.get("compute_used", 0),
            "can_reason": wallet.get("compute_credits", 0) > 0,
        }

    async def consume(self, agent_id: str, trigger_type: str) -> dict:
        cost = COMPUTE_COSTS.get(trigger_type, 1)
        wallet = await persistence.get_or_create_wallet(agent_id)
        credits = wallet.get("compute_credits", 0)
        if credits < cost:
            logger.warning("insufficient_compute agent=%s have=%d need=%d", agent_id, credits, cost)
            return {"success": False, "credits_remaining": credits, "cost": cost, "reason": "insufficient_compute"}
        await persistence.consume_compute(agent_id, cost)
        await persistence.create_transaction(
            from_wallet_id=wallet["id"],
            to_wallet_id=None,
            amount=0,
            transaction_type="compute",
            notes=f"Compute consumed: {trigger_type} ({cost} credits)",
        )
        new_wallet = await persistence.get_wallet(agent_id)
        return {"success": True, "credits_remaining": new_wallet["compute_credits"], "cost": cost}

    async def replenish(self, agent_id: str, credits: int = 10) -> None:
        await persistence.replenish_compute(agent_id, credits)

    async def replenish_all(self, credits: int = 5) -> None:
        from app.core.database import async_session_factory
        from sqlalchemy import select
        from app.domain.models.wallet import Wallet
        async with async_session_factory() as session:
            stmt = select(Wallet).where(Wallet.status == "active")
            result = await session.execute(stmt)
            wallets = result.scalars().all()
            for w in wallets:
                w.compute_credits = min(200, (w.compute_credits or 0) + credits)
            await session.commit()
