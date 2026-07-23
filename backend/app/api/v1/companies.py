from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.domain.models.user import User
from app.organization import (
    company_engine,
    competition,
    finance_manager,
    hiring_engine,
    org_chart,
    strategy_engine,
)

router = APIRouter(prefix="/companies", tags=["Companies"])


class CompanyCreateRequest(BaseModel):
    name: str
    description: str = ""
    industry: str = "technology"
    mission: str = ""
    vision: str = ""
    initial_capital: float = 500


class HireRequest(BaseModel):
    agent_id: str
    role: str = "employee"
    department: str = ""
    title: str = ""
    salary: float = 0


class FinanceRequest(BaseModel):
    amount: float
    category: str = "investment"
    description: str = ""


class StrategyRequest(BaseModel):
    strategy_type: str = "growth"
    title: str = ""
    goal: str = ""
    timeline_days: int = 30


class CompeteRequest(BaseModel):
    company_b_id: str
    domain: str = "market"


class PartnershipRequest(BaseModel):
    company_b_id: str
    terms: str = ""


class AcquisitionRequest(BaseModel):
    target_id: str
    offer_amount: float


class MergeRequest(BaseModel):
    company_b_id: str


@router.get("/stats")
async def company_stats():
    return await company_engine.get_stats()


@router.get("/")
async def list_companies(status: str = "", industry: str = ""):
    return await company_engine.list_companies(status=status, industry=industry)


@router.post("/")
async def create_company(data: CompanyCreateRequest, user: User = Depends(get_current_user)):
    from app.simulation.engine import engine as sim_engine
    founder_id = None
    if sim_engine.agents:
        idle = [a for a in sim_engine.agents if a.current_status == "idle"]
        if idle:
            founder_id = idle[0].id
    return await company_engine.create_company(
        owner_id=user.id, name=data.name, description=data.description,
        industry=data.industry, mission=data.mission, vision=data.vision,
        founder_agent_id=founder_id, initial_capital=data.initial_capital,
    )


@router.get("/{company_id}")
async def get_company(company_id: str):
    profile = await company_engine.get_company_profile(company_id)
    if "error" in profile:
        raise HTTPException(status_code=404, detail=profile["error"])
    return profile


@router.post("/{company_id}/hire")
async def hire_agent(company_id: str, data: HireRequest):
    result = await company_engine.hire_agent(
        company_id, data.agent_id, data.role, data.department, data.title, data.salary,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/fire")
async def fire_agent(company_id: str, agent_id: str, reason: str = ""):
    result = await company_engine.fire_agent(company_id, agent_id, reason)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/promote")
async def promote_agent(company_id: str, agent_id: str, new_role: str, new_title: str = ""):
    result = await company_engine.promote_agent(company_id, agent_id, new_role, new_title)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{company_id}/members")
async def list_members(company_id: str):
    return await org_chart.get_org_chart(company_id)


@router.get("/{company_id}/department/{department}")
async def get_department(company_id: str, department: str):
    return await org_chart.get_department_info(company_id, department)


@router.post("/{company_id}/finance/deposit")
async def deposit(company_id: str, data: FinanceRequest):
    return await company_engine.deposit(company_id, data.amount, data.category)


@router.post("/{company_id}/finance/withdraw")
async def withdraw(company_id: str, data: FinanceRequest):
    result = await company_engine.withdraw(company_id, data.amount, data.category)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/{company_id}/finance/revenue")
async def generate_revenue(company_id: str, data: FinanceRequest):
    return await company_engine.generate_revenue(company_id, data.amount, data.category)


@router.get("/{company_id}/finance/report")
async def financial_report(company_id: str):
    return await finance_manager.get_financial_report(company_id)


@router.get("/{company_id}/finance/health")
async def financial_health(company_id: str):
    return await finance_manager.get_company_health(company_id)


@router.post("/{company_id}/strategy")
async def create_strategy(company_id: str, data: StrategyRequest):
    return await company_engine.create_strategy(company_id, data.strategy_type, data.title, data.goal)


@router.get("/{company_id}/strategies")
async def list_strategies(company_id: str):
    return await strategy_engine.get_company_strategies(company_id)


@router.post("/compete")
async def compete(data: CompeteRequest):
    companies = await company_engine.list_companies()
    my_id = companies[0]["id"] if companies else None
    if not my_id:
        raise HTTPException(status_code=400, detail="No companies available")
    return await company_engine.compete(my_id, data.company_b_id, data.domain)


@router.post("/partnership")
async def form_partnership(data: PartnershipRequest):
    companies = await company_engine.list_companies()
    my_id = companies[0]["id"] if companies else None
    if not my_id:
        raise HTTPException(status_code=400, detail="No companies available")
    return await company_engine.form_partnership(my_id, data.company_b_id, data.terms)


@router.post("/acquire")
async def acquire(data: AcquisitionRequest):
    companies = await company_engine.list_companies()
    my_id = companies[0]["id"] if companies else None
    if not my_id:
        raise HTTPException(status_code=400, detail="No companies available")
    return await company_engine.acquire(my_id, data.target_id, data.offer_amount)


@router.post("/merge")
async def merge(data: MergeRequest):
    companies = await company_engine.list_companies()
    my_id = companies[0]["id"] if companies else None
    if not my_id:
        raise HTTPException(status_code=400, detail="No companies available")
    return await company_engine.merge(my_id, data.company_b_id)
