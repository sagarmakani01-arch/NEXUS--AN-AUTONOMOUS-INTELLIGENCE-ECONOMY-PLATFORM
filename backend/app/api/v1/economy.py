from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/economy", tags=["Autonomous Economy"])


class CreateLoanRequest(BaseModel):
    borrower_id: str
    borrower_type: str = "agent"
    amount: float
    term_days: int = 30


class RepayLoanRequest(BaseModel):
    loan_id: str
    amount: float


class SavingsRequest(BaseModel):
    agent_id: str
    amount: float


class InvestmentRequest(BaseModel):
    investor_id: str
    investor_type: str = "agent"
    target_id: str
    target_type: str = "company"
    amount: float
    risk_level: str = "medium"


@router.get("/engine/state")
async def get_engine_state():
    from app.economy.engine import economy_engine
    return economy_engine.get_state()


@router.get("/markets")
async def list_markets(market_type: str | None = None):
    from app.economy.market_engine import market_engine
    return await market_engine.get_all_markets(market_type)


@router.get("/markets/{market_id}")
async def get_market(market_id: str):
    from app.economy.market_engine import market_engine
    market = await market_engine.get_market_data(market_id)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/markets/{market_id}/history")
async def get_price_history(market_id: str, limit: int = 50):
    from app.economy import persistence as eco_db
    return await eco_db.get_price_history(market_id, limit)


@router.get("/resources")
async def get_resource_status():
    from app.economy.resource_economy import resource_economy
    return resource_economy.get_resource_status()


@router.get("/resources/state")
async def get_resource_state():
    from app.economy.resource_economy import resource_economy
    return resource_economy.get_state()


@router.post("/finance/loan")
async def issue_loan(req: CreateLoanRequest):
    from app.economy.finance import finance_engine
    return await finance_engine.issue_loan(
        borrower_id=req.borrower_id, borrower_type=req.borrower_type,
        amount=req.amount, term_days=req.term_days,
    )


@router.post("/finance/repay")
async def repay_loan(req: RepayLoanRequest):
    from app.economy.finance import finance_engine
    return await finance_engine.repay_loan(req.loan_id, req.amount)


@router.post("/finance/savings")
async def process_savings(req: SavingsRequest):
    from app.economy.finance import finance_engine
    return await finance_engine.process_savings(req.agent_id, req.amount)


@router.get("/finance/overview")
async def get_financial_overview():
    from app.economy.finance import finance_engine
    return await finance_engine.get_financial_overview()


@router.post("/investments")
async def make_investment(req: InvestmentRequest):
    from app.economy.investment import investment_engine
    return await investment_engine.make_investment(
        investor_id=req.investor_id, investor_type=req.investor_type,
        target_id=req.target_id, target_type=req.target_type,
        amount=req.amount, risk_level=req.risk_level,
    )


@router.post("/investments/{investment_id}/mature")
async def mature_investment(investment_id: str):
    from app.economy.investment import investment_engine
    return await investment_engine.mature_investment(investment_id)


@router.get("/investments/agent/{agent_id}")
async def get_agent_investments(agent_id: str):
    from app.economy.investment import investment_engine
    return await investment_engine.get_agent_investments(agent_id)


@router.get("/investments/market")
async def get_market_investments():
    from app.economy.investment import investment_engine
    return await investment_engine.get_market_investments()


@router.get("/wealth")
async def get_wealth_distribution():
    from app.economy.wealth import wealth_distribution
    return await wealth_distribution.analyze()


@router.get("/wealth/trend")
async def get_wealth_trend():
    from app.economy.wealth import wealth_distribution
    return wealth_distribution.get_wealth_trend()


@router.get("/events")
async def get_economic_events(event_type: str | None = None, status: str | None = None):
    from app.economy import persistence as eco_db
    return await eco_db.get_economic_events(event_type, status)


@router.get("/indicators")
async def get_indicators(indicator_type: str | None = None):
    from app.economy import persistence as eco_db
    return await eco_db.get_indicators(indicator_type)


@router.get("/intelligence/trends")
async def get_market_trends():
    from app.economy.intelligence import economic_intelligence
    return await economic_intelligence.get_market_trends()


@router.get("/intelligence/price-changes")
async def get_price_changes():
    from app.economy.intelligence import economic_intelligence
    return await economic_intelligence.get_price_changes()


@router.get("/intelligence/opportunities")
async def get_investment_opportunities():
    from app.economy.intelligence import economic_intelligence
    return await economic_intelligence.get_investment_opportunities()


@router.get("/intelligence/industry/{industry}")
async def get_industry_report(industry: str):
    from app.economy.intelligence import economic_intelligence
    return await economic_intelligence.get_industry_report(industry)


@router.get("/dashboard")
async def get_economic_dashboard():
    from app.economy.intelligence import economic_intelligence
    return await economic_intelligence.get_economic_dashboard()


@router.get("/stats")
async def get_economy_stats():
    from app.economy import persistence as eco_db
    return await eco_db.get_economy_stats()


@router.get("/pricing/state")
async def get_pricing_state():
    from app.economy.pricing import pricing_engine
    return pricing_engine.get_state()
