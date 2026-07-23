from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.resources.analytics import FinancialAnalytics
from app.resources.asset_manager import AssetManager
from app.resources.compute_manager import ComputeManager
from app.resources.wallet_manager import WalletManager

logger = logging.getLogger("nexus.resources")


class ResourceManager:
    def __init__(self) -> None:
        self.wallet = WalletManager()
        self.compute = ComputeManager()
        self.asset = AssetManager()
        self.analytics = FinancialAnalytics()

    async def init_agent(self, agent_id: str, initial_balance: float = 100.0, compute_credits: int = 100) -> dict:
        wallet = await self.wallet.get_wallet(agent_id)
        if wallet and wallet.get("balance", 0) > 0:
            return wallet
        wallet = await self.wallet.credit(agent_id, initial_balance, reason="Initial deposit", tx_type="income")
        logger.info("agent_wallet_initialized agent=%s balance=%.0f", agent_id, initial_balance)
        return wallet

    async def on_work_completed(self, agent_id: str, reward: float, goal: str = "") -> dict:
        wallet = await self.wallet.credit(agent_id, reward, reason=f"Work completed: {goal}", tx_type="salary")
        return wallet

    async def on_expense(self, agent_id: str, amount: float, category: str, description: str = "") -> dict:
        try:
            wallet = await self.wallet.debit(agent_id, amount, reason=description or category, tx_type="expense")
            return wallet
        except ValueError as e:
            logger.warning("expense_failed agent=%s err=%s", agent_id, e)
            return {"error": str(e)}

    async def on_daily_maintenance(self, agent_id: str) -> dict:
        assets = await self.asset.get_assets(agent_id)
        total_maintenance = sum(a.get("maintenance_cost", 0) for a in assets if a.get("status") == "active")
        compute_cost = 2
        total_cost = total_maintenance + compute_cost
        results = {"maintenance_cost": total_maintenance, "compute_cost": compute_cost}
        if total_cost > 0:
            try:
                await self.wallet.debit(agent_id, total_cost, reason="Daily maintenance", tx_type="expense")
            except ValueError:
                results["maintenance_skipped"] = True
        await self.compute.replenish(agent_id, 5)
        await self.compute.consume(agent_id, "simple_decision")
        return results

    async def process_daily(self, agent_ids: list[str]) -> None:
        for agent_id in agent_ids:
            try:
                await self.on_daily_maintenance(agent_id)
            except Exception as exc:
                logger.error("daily_maintenance_error agent=%s err=%s", agent_id, exc)
        await self.compute.replenish_all(credits=5)

    async def get_full_state(self, agent_id: str) -> dict:
        summary = await self.analytics.get_financial_summary(agent_id)
        daily = await self.analytics.get_daily_summary(agent_id)
        compute = await self.analytics.get_compute_analytics(agent_id)
        allocation = await self.analytics.get_resource_allocation(agent_id)
        return {
            "wallet": summary,
            "daily": daily,
            "compute": compute,
            "allocation": allocation,
        }

    async def get_wallet_info(self, agent_id: str) -> dict:
        return await self.wallet.get_wallet(agent_id)

    async def transfer(self, from_agent: str, to_agent: str, amount: float, reason: str = "") -> dict:
        return await self.wallet.transfer(from_agent, to_agent, amount, reason)

    async def get_transactions(self, agent_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
        return await self.wallet.get_transaction_history(agent_id, limit, offset)

    async def get_assets(self, agent_id: str) -> list[dict]:
        return await self.asset.get_assets(agent_id)

    async def purchase_asset(self, agent_id: str, asset_type: str, name: str, description: str = "", quantity: int = 1) -> dict:
        return await self.asset.purchase_asset(agent_id, asset_type, name, description, quantity)

    async def sell_asset(self, agent_id: str, asset_id: str) -> dict:
        return await self.asset.sell_asset(agent_id, asset_id)

    async def consume_compute(self, agent_id: str, trigger_type: str) -> dict:
        return await self.compute.consume(agent_id, trigger_type)

    async def get_compute_balance(self, agent_id: str) -> dict:
        return await self.compute.get_balance(agent_id)

    async def get_analytics(self, agent_id: str) -> dict:
        return await self.analytics.get_financial_summary(agent_id)

    async def get_daily_analytics(self, agent_id: str) -> dict:
        return await self.analytics.get_daily_summary(agent_id)

    async def get_monthly_trends(self, agent_id: str) -> list[dict]:
        return await self.analytics.get_monthly_trends(agent_id)

    async def get_all_wallets(self, limit: int = 100, offset: int = 0) -> list[dict]:
        return await self.wallet.get_wallets(limit, offset)


resource_manager = ResourceManager()
