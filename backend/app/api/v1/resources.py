from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.resources.manager import resource_manager

router = APIRouter(prefix="/resources", tags=["resources"])


class TransferRequest(BaseModel):
    from_agent: str
    to_agent: str
    amount: float
    reason: str = ""


class PurchaseAssetRequest(BaseModel):
    agent_id: str
    asset_type: str
    name: str
    description: str = ""
    quantity: int = 1


class SellAssetRequest(BaseModel):
    agent_id: str
    asset_id: str


@router.get("/wallet/{agent_id}")
async def get_wallet(agent_id: str):
    wallet = await resource_manager.get_wallet_info(agent_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet


@router.get("/wallet/{agent_id}/transactions")
async def get_transactions(
    agent_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    transactions = await resource_manager.get_transactions(agent_id, limit, offset)
    return {"transactions": transactions, "total": len(transactions)}


@router.post("/transfer")
async def transfer(request: TransferRequest):
    try:
        result = await resource_manager.transfer(
            request.from_agent, request.to_agent, request.amount, request.reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compute/{agent_id}")
async def get_compute_balance(agent_id: str):
    return await resource_manager.get_compute_balance(agent_id)


@router.get("/assets/{agent_id}")
async def get_assets(agent_id: str):
    assets = await resource_manager.get_assets(agent_id)
    return {"assets": assets, "total": len(assets)}


@router.post("/assets/purchase")
async def purchase_asset(request: PurchaseAssetRequest):
    try:
        result = await resource_manager.purchase_asset(
            request.agent_id, request.asset_type, request.name,
            request.description, request.quantity,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assets/sell")
async def sell_asset(request: SellAssetRequest):
    try:
        result = await resource_manager.sell_asset(request.agent_id, request.asset_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics/{agent_id}")
async def get_analytics(agent_id: str):
    return await resource_manager.get_analytics(agent_id)


@router.get("/analytics/{agent_id}/daily")
async def get_daily_analytics(agent_id: str):
    return await resource_manager.get_daily_analytics(agent_id)


@router.get("/analytics/{agent_id}/trends")
async def get_monthly_trends(agent_id: str):
    trends = await resource_manager.get_monthly_trends(agent_id)
    return {"trends": trends}


@router.get("/analytics/{agent_id}/allocation")
async def get_resource_allocation(agent_id: str):
    return await resource_manager.get_analytics(agent_id)


@router.get("/summary/{agent_id}")
async def get_full_state(agent_id: str):
    return await resource_manager.get_full_state(agent_id)


@router.get("/wallets")
async def get_all_wallets(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    wallets = await resource_manager.get_all_wallets(limit, offset)
    return {"wallets": wallets, "total": len(wallets)}
