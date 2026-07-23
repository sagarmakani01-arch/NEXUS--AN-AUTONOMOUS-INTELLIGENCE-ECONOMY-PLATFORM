import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_, or_

from app.core.database import async_session_factory
from app.domain.models.economy import (
    Market, PriceHistory, Investment, Loan, EconomicIndicator, EconomicEvent,
)

logger = logging.getLogger("nexus.economy")


async def create_market(name: str, market_type: str, description: str | None = None,
                        base_price: float = 10.0) -> str:
    async with async_session_factory() as session:
        market = Market(
            name=name, market_type=market_type,
            description=description, base_price=base_price,
            current_price=base_price,
        )
        session.add(market)
        await session.commit()
        return market.id


async def get_market(market_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Market).where(Market.id == market_id))
        m = result.scalar_one_or_none()
        if not m:
            return None
        return _market_to_dict(m)


async def get_market_by_name(name: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Market).where(Market.name == name))
        m = result.scalar_one_or_none()
        if not m:
            return None
        return _market_to_dict(m)


async def list_markets(market_type: str | None = None, status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Market).where(Market.status == status)
        if market_type:
            stmt = stmt.where(Market.market_type == market_type)
        stmt = stmt.order_by(Market.volume.desc())
        result = await session.execute(stmt)
        return [_market_to_dict(m) for m in result.scalars().all()]


async def update_market(market_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Market).where(Market.id == market_id))
        m = result.scalar_one_or_none()
        if m:
            for k, v in kwargs.items():
                if hasattr(m, k):
                    setattr(m, k, v)
            m.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def record_price_history(market_id: str, price: float, supply: int, demand: int,
                               volume: int, change_pct: float = 0.0) -> str:
    async with async_session_factory() as session:
        ph = PriceHistory(
            market_id=market_id, price=price,
            supply=supply, demand=demand,
            volume=volume, change_pct=change_pct,
        )
        session.add(ph)
        await session.commit()
        return ph.id


async def get_price_history(market_id: str, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        result = await session.execute(
            select(PriceHistory)
            .where(PriceHistory.market_id == market_id)
            .order_by(PriceHistory.recorded_at.desc())
            .limit(limit)
        )
        return [
            {
                "id": ph.id, "market_id": ph.market_id,
                "price": ph.price, "supply": ph.supply,
                "demand": ph.demand, "volume": ph.volume,
                "change_pct": ph.change_pct,
                "recorded_at": ph.recorded_at.isoformat() if ph.recorded_at else None,
            }
            for ph in result.scalars().all()
        ]


async def create_investment(investor_id: str, investor_type: str, target_id: str,
                            target_type: str, amount: float,
                            expected_return_pct: float = 0.10,
                            risk_level: str = "medium") -> str:
    async with async_session_factory() as session:
        inv = Investment(
            investor_id=investor_id, investor_type=investor_type,
            target_id=target_id, target_type=target_type,
            amount=amount, expected_return_pct=expected_return_pct,
            risk_level=risk_level,
        )
        session.add(inv)
        await session.commit()
        return inv.id


async def get_investments(investor_id: str | None = None, target_id: str | None = None,
                          status: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Investment)
        conditions = []
        if investor_id:
            conditions.append(Investment.investor_id == investor_id)
        if target_id:
            conditions.append(Investment.target_id == target_id)
        if status:
            conditions.append(Investment.status == status)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Investment.invested_at.desc())
        result = await session.execute(stmt)
        return [
            {
                "id": i.id, "investor_id": i.investor_id, "investor_type": i.investor_type,
                "target_id": i.target_id, "target_type": i.target_type,
                "amount": i.amount, "expected_return_pct": i.expected_return_pct,
                "actual_return": i.actual_return, "risk_level": i.risk_level,
                "status": i.status,
                "invested_at": i.invested_at.isoformat() if i.invested_at else None,
            }
            for i in result.scalars().all()
        ]


async def update_investment(investment_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Investment).where(Investment.id == investment_id))
        inv = result.scalar_one_or_none()
        if inv:
            for k, v in kwargs.items():
                if hasattr(inv, k):
                    setattr(inv, k, v)
            await session.commit()


async def create_loan(borrower_id: str, borrower_type: str, amount: float,
                      interest_rate: float = 0.05, term_days: int = 30,
                      lender_id: str = "bank") -> str:
    async with async_session_factory() as session:
        loan = Loan(
            borrower_id=borrower_id, borrower_type=borrower_type,
            lender_id=lender_id, amount=amount,
            interest_rate=interest_rate, term_days=term_days,
        )
        session.add(loan)
        await session.commit()
        return loan.id


async def get_loans(borrower_id: str | None = None, status: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Loan)
        conditions = []
        if borrower_id:
            conditions.append(Loan.borrower_id == borrower_id)
        if status:
            conditions.append(Loan.status == status)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Loan.issued_at.desc())
        result = await session.execute(stmt)
        return [
            {
                "id": l.id, "borrower_id": l.borrower_id, "borrower_type": l.borrower_type,
                "lender_id": l.lender_id, "amount": l.amount,
                "interest_rate": l.interest_rate, "term_days": l.term_days,
                "amount_paid": l.amount_paid, "status": l.status,
                "issued_at": l.issued_at.isoformat() if l.issued_at else None,
                "due_at": l.due_at.isoformat() if l.due_at else None,
            }
            for l in result.scalars().all()
        ]


async def update_loan(loan_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Loan).where(Loan.id == loan_id))
        loan = result.scalar_one_or_none()
        if loan:
            for k, v in kwargs.items():
                if hasattr(loan, k):
                    setattr(loan, k, v)
            await session.commit()


async def record_indicator(indicator_type: str, value: float, previous_value: float | None = None,
                           period: str = "daily", metadata: dict | None = None) -> str:
    async with async_session_factory() as session:
        change_pct = 0.0
        if previous_value and previous_value != 0:
            change_pct = round((value - previous_value) / previous_value * 100, 2)
        ind = EconomicIndicator(
            indicator_type=indicator_type, value=value,
            previous_value=previous_value, change_pct=change_pct,
            period=period, metadata_json=json.dumps(metadata or {}),
        )
        session.add(ind)
        await session.commit()
        return ind.id


async def get_indicators(indicator_type: str | None = None, limit: int = 30) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(EconomicIndicator)
        if indicator_type:
            stmt = stmt.where(EconomicIndicator.indicator_type == indicator_type)
        stmt = stmt.order_by(EconomicIndicator.recorded_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return [
            {
                "id": i.id, "indicator_type": i.indicator_type,
                "value": i.value, "previous_value": i.previous_value,
                "change_pct": i.change_pct, "period": i.period,
                "recorded_at": i.recorded_at.isoformat() if i.recorded_at else None,
            }
            for i in result.scalars().all()
        ]


async def get_latest_indicator(indicator_type: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(
            select(EconomicIndicator)
            .where(EconomicIndicator.indicator_type == indicator_type)
            .order_by(EconomicIndicator.recorded_at.desc())
            .limit(1)
        )
        ind = result.scalar_one_or_none()
        if not ind:
            return None
        return {
            "id": ind.id, "indicator_type": ind.indicator_type,
            "value": ind.value, "previous_value": ind.previous_value,
            "change_pct": ind.change_pct,
            "recorded_at": ind.recorded_at.isoformat() if ind.recorded_at else None,
        }


async def record_economic_event(event_type: str, title: str, description: str | None = None,
                                severity: str = "medium", affected_markets: list[str] | None = None,
                                affected_sectors: list[str] | None = None,
                                impact_magnitude: float = 0.0,
                                metadata: dict | None = None) -> str:
    async with async_session_factory() as session:
        ev = EconomicEvent(
            event_type=event_type, title=title,
            description=description, severity=severity,
            affected_markets=json.dumps(affected_markets or []),
            affected_sectors=json.dumps(affected_sectors or []),
            impact_magnitude=impact_magnitude,
            metadata_json=json.dumps(metadata or {}),
        )
        session.add(ev)
        await session.commit()
        return ev.id


async def get_economic_events(event_type: str | None = None, status: str | None = None,
                              limit: int = 20) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(EconomicEvent)
        conditions = []
        if event_type:
            conditions.append(EconomicEvent.event_type == event_type)
        if status:
            conditions.append(EconomicEvent.status == status)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(EconomicEvent.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return [
            {
                "id": e.id, "event_type": e.event_type,
                "severity": e.severity, "title": e.title,
                "description": e.description,
                "affected_markets": json.loads(e.affected_markets) if e.affected_markets else [],
                "affected_sectors": json.loads(e.affected_sectors) if e.affected_sectors else [],
                "impact_magnitude": e.impact_magnitude,
                "status": e.status,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in result.scalars().all()
        ]


async def get_economy_stats() -> dict:
    async with async_session_factory() as session:
        market_count = await session.execute(select(func.count(Market.id)))
        inv_count = await session.execute(select(func.count(Investment.id)))
        loan_count = await session.execute(select(func.count(Loan.id)))
        event_count = await session.execute(select(func.count(EconomicEvent.id)))
        total_invested = await session.execute(
            select(func.sum(Investment.amount)).where(Investment.status == "active")
        )
        total_loaned = await session.execute(
            select(func.sum(Loan.amount)).where(Loan.status == "active")
        )
        return {
            "total_markets": market_count.scalar() or 0,
            "total_investments": inv_count.scalar() or 0,
            "total_loans": loan_count.scalar() or 0,
            "total_economic_events": event_count.scalar() or 0,
            "total_invested_volume": total_invested.scalar() or 0.0,
            "total_loan_volume": total_loaned.scalar() or 0.0,
        }


def _market_to_dict(m: Market) -> dict:
    return {
        "id": m.id, "name": m.name, "market_type": m.market_type,
        "description": m.description, "current_price": m.current_price,
        "base_price": m.base_price, "supply": m.supply,
        "demand": m.demand, "volume": m.volume,
        "growth_rate": m.growth_rate, "volatility": m.volatility,
        "status": m.status,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }
