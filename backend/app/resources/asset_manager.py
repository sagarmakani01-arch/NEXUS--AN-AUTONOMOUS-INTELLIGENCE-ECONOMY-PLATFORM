from __future__ import annotations
import logging
from app.resources import persistence

logger = logging.getLogger("nexus.resources.assets")

ASSET_CATALOG = {
    "knowledge_license": {"base_price": 100, "maintenance": 5, "depreciation": 0.02},
    "software_tool": {"base_price": 200, "maintenance": 10, "depreciation": 0.05},
    "patent": {"base_price": 500, "maintenance": 20, "depreciation": 0.01},
    "company_share": {"base_price": 0, "maintenance": 0, "depreciation": 0},
    "equipment": {"base_price": 150, "maintenance": 8, "depreciation": 0.03},
    "research_asset": {"base_price": 300, "maintenance": 15, "depreciation": 0.02},
}

class AssetManager:
    async def purchase_asset(self, agent_id: str, asset_type: str, name: str, description: str = "", quantity: int = 1) -> dict:
        catalog = ASSET_CATALOG.get(asset_type)
        if not catalog:
            raise ValueError(f"Unknown asset type: {asset_type}")
        from app.resources.wallet_manager import WalletManager
        wm = WalletManager()
        total_cost = catalog["base_price"] * quantity
        wallet = await wm.get_wallet(agent_id)
        if wallet["balance"] < total_cost:
            raise ValueError(f"Insufficient funds: {wallet['balance']:.2f} < {total_cost:.2f}")
        await wm.debit(agent_id, total_cost, reason=f"Purchased {name}", tx_type="purchase")
        asset_id = await persistence.create_asset(
            agent_id=agent_id,
            asset_type=asset_type,
            name=name,
            description=description,
            value=catalog["base_price"] * quantity,
            purchase_price=total_cost,
            maintenance_cost=catalog["maintenance"] * quantity,
            quantity=quantity,
        )
        return {"asset_id": asset_id, "cost": total_cost, "maintenance_per_day": catalog["maintenance"] * quantity}

    async def sell_asset(self, agent_id: str, asset_id: str) -> dict:
        asset = await persistence.sell_asset(asset_id)
        if not asset:
            raise ValueError("Asset not found")
        sell_price = asset["value"] * 0.7
        from app.resources.wallet_manager import WalletManager
        wm = WalletManager()
        await wm.credit(agent_id, sell_price, reason=f"Sold {asset['name']}", tx_type="income")
        return {"asset_id": asset_id, "sold_for": sell_price}

    async def get_assets(self, agent_id: str) -> list[dict]:
        return await persistence.get_agent_assets(agent_id)

    async def get_total_value(self, agent_id: str) -> float:
        return await persistence.get_asset_total_value(agent_id)

    async def calculate_maintenance_costs(self, agent_id: str) -> float:
        assets = await persistence.get_agent_assets(agent_id)
        return sum(a.get("maintenance_cost", 0) for a in assets if a.get("status") == "active")
