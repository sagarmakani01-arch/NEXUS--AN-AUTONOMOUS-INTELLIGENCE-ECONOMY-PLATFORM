from __future__ import annotations
import logging
from app.resources import persistence

logger = logging.getLogger("nexus.resources.wallet")

class WalletManager:
    async def get_wallet(self, agent_id: str) -> dict:
        wallet = await persistence.get_or_create_wallet(agent_id)
        return wallet

    async def get_balance(self, agent_id: str) -> float:
        wallet = await persistence.get_or_create_wallet(agent_id)
        return wallet.get("balance", 0)

    async def credit(self, agent_id: str, amount: float, reason: str = "", tx_type: str = "income") -> dict:
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
        wallet = await persistence.get_or_create_wallet(agent_id)
        await persistence.update_balance(agent_id, amount)
        await persistence.create_transaction(
            from_wallet_id=None,
            to_wallet_id=wallet["id"],
            amount=amount,
            transaction_type=tx_type,
            notes=reason,
        )
        return await persistence.get_wallet(agent_id)

    async def debit(self, agent_id: str, amount: float, reason: str = "", tx_type: str = "expense") -> dict:
        if amount <= 0:
            raise ValueError("Debit amount must be positive")
        wallet = await persistence.get_or_create_wallet(agent_id)
        if wallet["balance"] < amount:
            raise ValueError(f"Insufficient balance: {wallet['balance']:.2f} < {amount:.2f}")
        await persistence.update_balance(agent_id, -amount)
        await persistence.create_transaction(
            from_wallet_id=wallet["id"],
            to_wallet_id=None,
            amount=amount,
            transaction_type=tx_type,
            notes=reason,
        )
        return await persistence.get_wallet(agent_id)

    async def transfer(self, from_agent: str, to_agent: str, amount: float, reason: str = "") -> dict:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive")
        from_wallet = await persistence.get_or_create_wallet(from_agent)
        to_wallet = await persistence.get_or_create_wallet(to_agent)
        if from_wallet["balance"] < amount:
            raise ValueError(f"Insufficient balance: {from_wallet['balance']:.2f} < {amount:.2f}")
        await persistence.update_balance(from_agent, -amount)
        await persistence.update_balance(to_agent, amount)
        tx_id = await persistence.create_transaction(
            from_wallet_id=from_wallet["id"],
            to_wallet_id=to_wallet["id"],
            amount=amount,
            transaction_type="transfer",
            notes=reason,
        )
        return {"transfer_id": tx_id, "from_balance": from_wallet["balance"] - amount, "to_balance": to_wallet["balance"] + amount}

    async def reserve(self, agent_id: str, amount: float) -> bool:
        return await persistence.reserve_funds(agent_id, amount)

    async def release(self, agent_id: str, amount: float) -> bool:
        return await persistence.release_reserved(agent_id, amount)

    async def get_transaction_history(self, agent_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
        return await persistence.get_agent_transactions(agent_id, limit, offset)

    async def get_wallets(self, limit: int = 100, offset: int = 0) -> list[dict]:
        return await persistence.get_all_wallets(limit, offset)
