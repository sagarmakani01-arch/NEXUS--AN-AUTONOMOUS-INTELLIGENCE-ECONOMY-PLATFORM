import logging
import random

from app.economy import persistence as eco_db
from app.economy.pricing import pricing_engine
from app.resources.persistence import get_wallet, update_balance, create_transaction
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.economy.investment")


class InvestmentEngine:
    def __init__(self):
        self.stats = {
            "investments_made": 0,
            "investments_matured": 0,
            "total_invested": 0.0,
            "total_returns": 0.0,
        }

    async def make_investment(self, investor_id: str, investor_type: str,
                              target_id: str, target_type: str,
                              amount: float, risk_level: str = "medium") -> dict:
        wallet = await get_wallet(investor_id)
        if not wallet or wallet.get("balance", 0) < amount:
            return {"success": False, "error": "Insufficient funds"}

        if amount <= 0:
            return {"success": False, "error": "Invalid amount"}

        expected_return = random.uniform(0.05, 0.25) if risk_level == "medium" else random.uniform(0.02, 0.40)

        inv_id = await eco_db.create_investment(
            investor_id=investor_id, investor_type=investor_type,
            target_id=target_id, target_type=target_type,
            amount=amount, expected_return_pct=round(expected_return, 4),
            risk_level=risk_level,
        )

        await update_balance(investor_id, -amount)
        await create_transaction(
            from_wallet_id=investor_id, to_wallet_id=target_id,
            amount=amount, transaction_type="investment",
            notes=f"Investment in {target_id}: {amount} NXC at {risk_level} risk",
        )

        self.stats["investments_made"] += 1
        self.stats["total_invested"] += amount

        await dispatch(Event(EventType.INVESTMENT_MADE, {
            "investment_id": inv_id, "investor_id": investor_id,
            "target_id": target_id, "amount": amount,
            "risk_level": risk_level, "expected_return": expected_return,
        }))

        return {
            "success": True,
            "investment_id": inv_id,
            "amount": amount,
            "expected_return_pct": round(expected_return, 4),
            "risk_level": risk_level,
        }

    async def mature_investment(self, investment_id: str) -> dict:
        investments = await eco_db.get_investments(investment_id)
        if not investments:
            return {"success": False, "error": "Investment not found"}
        inv = investments[0]

        if inv["status"] != "active":
            return {"success": False, "error": "Investment not active"}

        result = pricing_engine.calculate_investment_return(
            inv["amount"], inv["risk_level"]
        )

        if result["success"]:
            return_amount = inv["amount"] + result["return_amount"]
            await update_balance(inv["investor_id"], return_amount)
            await create_transaction(
                from_wallet_id=inv["target_id"], to_wallet_id=inv["investor_id"],
                amount=return_amount, transaction_type="investment_return",
                notes=f"Investment return: {result['return_pct']:.2%} on {inv['amount']} NXC",
            )
            self.stats["total_returns"] += return_amount
        else:
            loss = inv["amount"] * abs(result["return_pct"])
            self.stats["total_returns"] -= loss

        await eco_db.update_investment(
            investment_id,
            actual_return=result["return_amount"],
            status="matured",
        )
        self.stats["investments_matured"] += 1

        return {
            "success": True,
            "investment_id": investment_id,
            "returned": result["success"],
            "return_pct": result["return_pct"],
            "return_amount": result["return_amount"],
        }

    async def get_agent_investments(self, agent_id: str) -> dict:
        active = await eco_db.get_investments(investor_id=agent_id, status="active")
        matured = await eco_db.get_investments(investor_id=agent_id, status="matured")

        total_invested = sum(i["amount"] for i in active)
        total_returns = sum(i["actual_return"] for i in matured)

        return {
            "agent_id": agent_id,
            "active_investments": active,
            "matured_investments": matured[:10],
            "total_active_invested": round(total_invested, 2),
            "total_matured_returns": round(total_returns, 2),
            "investment_count": len(active) + len(matured),
        }

    async def get_market_investments(self) -> dict:
        all_active = await eco_db.get_investments(status="active")
        all_matured = await eco_db.get_investments(status="matured")

        total_active = sum(i["amount"] for i in all_active)
        total_returns = sum(i["actual_return"] for i in all_matured)

        by_risk = {}
        for inv in all_active:
            risk = inv["risk_level"]
            if risk not in by_risk:
                by_risk[risk] = {"count": 0, "total_amount": 0}
            by_risk[risk]["count"] += 1
            by_risk[risk]["total_amount"] += inv["amount"]

        return {
            "total_active_investments": len(all_active),
            "total_matured_investments": len(all_matured),
            "total_active_volume": round(total_active, 2),
            "total_returns": round(total_returns, 2),
            "by_risk_level": by_risk,
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


investment_engine = InvestmentEngine()
