from __future__ import annotations
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from app.core.database import async_session_factory
from app.domain.models.wallet import Wallet
from app.domain.models.transaction import Transaction
from app.domain.models.asset import Asset

logger = logging.getLogger("nexus.resources.analytics")

class FinancialAnalytics:
    async def get_financial_summary(self, agent_id: str) -> dict:
        from app.resources.persistence import get_wallet, get_agent_assets
        wallet = await get_wallet(agent_id)
        assets = await get_agent_assets(agent_id)
        asset_value = sum(a.get("value", 0) for a in assets if a.get("status") == "active")
        net_worth = (wallet["balance"] if wallet else 0) + asset_value
        return {
            "agent_id": agent_id,
            "wallet_balance": wallet["balance"] if wallet else 0,
            "reserved_balance": wallet["reserved_balance"] if wallet else 0,
            "compute_credits": wallet["compute_credits"] if wallet else 0,
            "total_earned": wallet["total_earned"] if wallet else 0,
            "total_spent": wallet["total_spent"] if wallet else 0,
            "asset_value": asset_value,
            "asset_count": len(assets),
            "net_worth": round(net_worth, 2),
            "financial_health": self._calc_health(wallet, asset_value),
        }

    async def get_daily_summary(self, agent_id: str) -> dict:
        async with async_session_factory() as session:
            today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            stmt = select(Transaction).where(
                Transaction.created_at >= today,
                Transaction.notes.isnot(None),
            )
            result = await session.execute(stmt)
            txs = result.scalars().all()
            agent_wallet = await _get_wallet_id_for_agent(agent_id, session)
            income = sum(t.amount for t in txs if t.to_wallet_id == agent_wallet and t.transaction_type != "compute")
            expenses = sum(t.amount for t in txs if t.from_wallet_id == agent_wallet)
            compute_used = sum(1 for t in txs if t.from_wallet_id == agent_wallet and t.transaction_type == "compute")
            return {
                "agent_id": agent_id,
                "date": today.isoformat(),
                "income": round(income, 2),
                "expenses": round(expenses, 2),
                "net": round(income - expenses, 2),
                "compute_used": compute_used,
                "transaction_count": len([t for t in txs if t.from_wallet_id == agent_wallet or t.to_wallet_id == agent_wallet]),
            }

    async def get_monthly_trends(self, agent_id: str, days: int = 30) -> list[dict]:
        async with async_session_factory() as session:
            wallet_stmt = select(Wallet).where(Wallet.agent_id == agent_id)
            wallet_result = await session.execute(wallet_stmt)
            wallet = wallet_result.scalar_one_or_none()
            if not wallet:
                return []
            cutoff = datetime.now(timezone.utc) - timedelta(days=days)
            stmt = select(Transaction).where(Transaction.created_at >= cutoff)
            result = await session.execute(stmt)
            txs = result.scalars().all()
            daily: dict[str, dict] = {}
            for tx in txs:
                if tx.from_wallet_id != wallet.id and tx.to_wallet_id != wallet.id:
                    continue
                day_str = tx.created_at.strftime("%Y-%m-%d") if tx.created_at else "unknown"
                if day_str not in daily:
                    daily[day_str] = {"date": day_str, "income": 0, "expenses": 0, "compute_used": 0}
                if tx.to_wallet_id == wallet.id and tx.transaction_type != "compute":
                    daily[day_str]["income"] += tx.amount
                elif tx.from_wallet_id == wallet.id:
                    if tx.transaction_type == "compute":
                        daily[day_str]["compute_used"] += 1
                    else:
                        daily[day_str]["expenses"] += tx.amount
            return sorted(daily.values(), key=lambda x: x["date"])

    async def get_compute_analytics(self, agent_id: str) -> dict:
        async with async_session_factory() as session:
            wallet_stmt = select(Wallet).where(Wallet.agent_id == agent_id)
            wallet_result = await session.execute(wallet_stmt)
            wallet = wallet_result.scalar_one_or_none()
            if not wallet:
                return {"agent_id": agent_id, "compute_credits": 0, "compute_used": 0}
            return {
                "agent_id": agent_id,
                "compute_credits": wallet.compute_credits or 0,
                "compute_used": wallet.compute_used or 0,
                "total_compute_lifetime": (wallet.compute_credits or 0) + (wallet.compute_used or 0),
                "efficiency": round((wallet.compute_used or 0) / max((wallet.compute_credits or 0) + (wallet.compute_used or 0), 1), 3),
            }

    async def get_resource_allocation(self, agent_id: str) -> dict:
        summary = await self.get_financial_summary(agent_id)
        total = max(summary["net_worth"], 1)
        return {
            "agent_id": agent_id,
            "cash_allocation": round(summary["wallet_balance"] / total * 100, 1),
            "reserved_allocation": round(summary["reserved_balance"] / total * 100, 1),
            "asset_allocation": round(summary["asset_value"] / total * 100, 1),
            "compute_allocation": round(summary["compute_credits"] * 0.5 / total * 100, 1),
        }

    def _calc_health(self, wallet: dict | None, asset_value: float) -> str:
        if not wallet:
            return "unknown"
        balance = wallet.get("balance", 0)
        compute = wallet.get("compute_credits", 0)
        if balance > 500 and compute > 50:
            return "excellent"
        if balance > 200 and compute > 20:
            return "good"
        if balance > 50 and compute > 5:
            return "fair"
        if balance > 0:
            return "poor"
        return "critical"

async def _get_wallet_id_for_agent(agent_id: str, session) -> str | None:
    stmt = select(Wallet).where(Wallet.agent_id == agent_id)
    result = await session.execute(stmt)
    wallet = result.scalar_one_or_none()
    return wallet.id if wallet else None
