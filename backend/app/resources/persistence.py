from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from app.core.database import async_session_factory
from app.domain.models.wallet import Wallet
from app.domain.models.transaction import Transaction
from app.domain.models.asset import Asset

logger = logging.getLogger("nexus.resources.persistence")


def _wallet_to_dict(wallet: Wallet) -> dict:
    return {
        "id": wallet.id,
        "agent_id": wallet.agent_id,
        "balance": wallet.balance or 0.0,
        "reserved_balance": wallet.reserved_balance or 0.0,
        "compute_credits": wallet.compute_credits or 0,
        "compute_used": getattr(wallet, "compute_used", 0) or 0,
        "total_earned": getattr(wallet, "total_earned", 0.0) or 0.0,
        "total_spent": getattr(wallet, "total_spent", 0.0) or 0.0,
        "status": wallet.status or "active",
        "created_at": wallet.created_at.isoformat() if wallet.created_at else None,
        "updated_at": wallet.updated_at.isoformat() if wallet.updated_at else None,
    }


def _tx_to_dict(tx: Transaction) -> dict:
    return {
        "id": tx.id,
        "from_wallet_id": tx.from_wallet_id,
        "to_wallet_id": tx.to_wallet_id,
        "amount": tx.amount,
        "transaction_type": tx.transaction_type,
        "notes": tx.notes or "",
        "reference_id": getattr(tx, "reference_id", "") or "",
        "reference_type": getattr(tx, "reference_type", "") or "",
        "created_at": tx.created_at.isoformat() if tx.created_at else None,
    }


def _asset_to_dict(asset: Asset) -> dict:
    return {
        "id": asset.id,
        "agent_id": asset.agent_id,
        "asset_type": asset.asset_type,
        "name": asset.name,
        "description": getattr(asset, "description", "") or "",
        "value": asset.value or 0.0,
        "purchase_price": getattr(asset, "purchase_price", 0.0) or 0.0,
        "maintenance_cost": getattr(asset, "maintenance_cost", 0.0) or 0.0,
        "quantity": getattr(asset, "quantity", 1) or 1,
        "status": asset.status or "active",
        "created_at": asset.created_at.isoformat() if asset.created_at else None,
        "updated_at": asset.updated_at.isoformat() if asset.updated_at else None,
    }


async def get_wallet(agent_id: str) -> dict | None:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        result = await session.execute(stmt)
        wallet = result.scalar_one_or_none()
        if not wallet:
            return None
        return _wallet_to_dict(wallet)


async def get_or_create_wallet(agent_id: str, initial_balance: float = 100.0) -> dict:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        result = await session.execute(stmt)
        wallet = result.scalar_one_or_none()
        if wallet:
            return _wallet_to_dict(wallet)
        wallet = Wallet(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            balance=initial_balance,
            reserved_balance=0.0,
            compute_credits=100,
            compute_used=0,
            total_earned=initial_balance,
            total_spent=0.0,
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(wallet)
        await session.commit()
        return _wallet_to_dict(wallet)


async def update_balance(agent_id: str, amount: float) -> dict:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        result = await session.execute(stmt)
        wallet = result.scalar_one_or_none()
        if not wallet:
            raise ValueError(f"Wallet not found for agent {agent_id}")
        wallet.balance = (wallet.balance or 0.0) + amount
        if amount > 0:
            wallet.total_earned = (wallet.total_earned or 0.0) + amount
        else:
            wallet.total_spent = (wallet.total_spent or 0.0) + abs(amount)
        wallet.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return _wallet_to_dict(wallet)


async def reserve_funds(agent_id: str, amount: float) -> bool:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        result = await session.execute(stmt)
        wallet = result.scalar_one_or_none()
        if not wallet or (wallet.balance or 0) < amount:
            return False
        wallet.balance = (wallet.balance or 0.0) - amount
        wallet.reserved_balance = (wallet.reserved_balance or 0.0) + amount
        wallet.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return True


async def release_reserved(agent_id: str, amount: float) -> bool:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        result = await session.execute(stmt)
        wallet = result.scalar_one_or_none()
        if not wallet or (wallet.reserved_balance or 0) < amount:
            return False
        wallet.reserved_balance = (wallet.reserved_balance or 0.0) - amount
        wallet.balance = (wallet.balance or 0.0) + amount
        wallet.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return True


async def consume_compute(agent_id: str, credits: int) -> bool:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        result = await session.execute(stmt)
        wallet = result.scalar_one_or_none()
        if not wallet or (wallet.compute_credits or 0) < credits:
            return False
        wallet.compute_credits = (wallet.compute_credits or 0) - credits
        wallet.compute_used = (getattr(wallet, "compute_used", 0) or 0) + credits
        wallet.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return True


async def replenish_compute(agent_id: str, credits: int) -> None:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        result = await session.execute(stmt)
        wallet = result.scalar_one_or_none()
        if wallet:
            wallet.compute_credits = min(200, (wallet.compute_credits or 0) + credits)
            wallet.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def get_all_wallets(limit: int = 100, offset: int = 0) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Wallet).where(Wallet.status == "active").offset(offset).limit(limit)
        result = await session.execute(stmt)
        wallets = result.scalars().all()
        return [_wallet_to_dict(w) for w in wallets]


async def create_transaction(
    from_wallet_id: str | None,
    to_wallet_id: str | None,
    amount: float,
    transaction_type: str,
    notes: str = "",
    reference_id: str = "",
    reference_type: str = "",
) -> str:
    async with async_session_factory() as session:
        tx = Transaction(
            id=str(uuid.uuid4()),
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id,
            amount=amount,
            transaction_type=transaction_type,
            notes=notes,
            reference_id=reference_id,
            reference_type=reference_type,
            created_at=datetime.now(timezone.utc),
        )
        session.add(tx)
        await session.commit()
        return tx.id


async def get_wallet_transactions(wallet_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
    async with async_session_factory() as session:
        stmt = (
            select(Transaction)
            .where((Transaction.from_wallet_id == wallet_id) | (Transaction.to_wallet_id == wallet_id))
            .order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        txs = result.scalars().all()
        return [_tx_to_dict(t) for t in txs]


async def get_agent_transactions(agent_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
    async with async_session_factory() as session:
        wallet_stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        wallet_result = await session.execute(wallet_stmt)
        wallet = wallet_result.scalar_one_or_none()
        if not wallet:
            return []
        stmt = (
            select(Transaction)
            .where((Transaction.from_wallet_id == wallet.id) | (Transaction.to_wallet_id == wallet.id))
            .order_by(Transaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await session.execute(stmt)
        txs = result.scalars().all()
        return [_tx_to_dict(t) for t in txs]


async def get_transactions_by_type(agent_id: str, tx_type: str, limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        wallet_stmt = select(Wallet).where(Wallet.agent_id == agent_id)
        wallet_result = await session.execute(wallet_stmt)
        wallet = wallet_result.scalar_one_or_none()
        if not wallet:
            return []
        stmt = (
            select(Transaction)
            .where(
                (Transaction.from_wallet_id == wallet.id) | (Transaction.to_wallet_id == wallet.id),
                Transaction.transaction_type == tx_type,
            )
            .order_by(Transaction.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        txs = result.scalars().all()
        return [_tx_to_dict(t) for t in txs]


async def create_asset(
    agent_id: str,
    asset_type: str,
    name: str,
    description: str,
    value: float,
    purchase_price: float,
    maintenance_cost: float = 0,
    quantity: int = 1,
) -> str:
    async with async_session_factory() as session:
        asset = Asset(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            asset_type=asset_type,
            name=name,
            description=description,
            value=value,
            purchase_price=purchase_price,
            maintenance_cost=maintenance_cost,
            quantity=quantity,
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(asset)
        await session.commit()
        return asset.id


async def get_agent_assets(agent_id: str) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Asset).where(Asset.agent_id == agent_id)
        result = await session.execute(stmt)
        assets = result.scalars().all()
        return [_asset_to_dict(a) for a in assets]


async def update_asset(asset_id: str, updates: dict) -> None:
    async with async_session_factory() as session:
        stmt = select(Asset).where(Asset.id == asset_id)
        result = await session.execute(stmt)
        asset = result.scalar_one_or_none()
        if not asset:
            return
        for key, value in updates.items():
            if hasattr(asset, key):
                setattr(asset, key, value)
        asset.updated_at = datetime.now(timezone.utc)
        await session.commit()


async def sell_asset(asset_id: str) -> dict | None:
    async with async_session_factory() as session:
        stmt = select(Asset).where(Asset.id == asset_id)
        result = await session.execute(stmt)
        asset = result.scalar_one_or_none()
        if not asset:
            return None
        asset.status = "sold"
        asset.updated_at = datetime.now(timezone.utc)
        await session.commit()
        return _asset_to_dict(asset)


async def get_asset_total_value(agent_id: str) -> float:
    async with async_session_factory() as session:
        stmt = select(Asset).where(Asset.agent_id == agent_id, Asset.status == "active")
        result = await session.execute(stmt)
        assets = result.scalars().all()
        return sum((a.value or 0.0) for a in assets)
