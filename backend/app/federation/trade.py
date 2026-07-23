import logging
import random

from app.federation import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.federation.trade")

TRADE_TYPES = ["knowledge", "technology", "compute", "resources", "products", "services"]
RESOURCE_TYPES = ["food", "energy", "minerals", "data", "innovation", "workforce"]


class TradeEngine:
    def __init__(self):
        self.stats = {"agreements_created": 0, "total_volume": 0}

    async def create_trade(self, civ_a_id: str, civ_b_id: str,
                           trade_type: str | None = None,
                           resource_offered: str | None = None,
                           resource_requested: str | None = None) -> dict:
        trade_type = trade_type or random.choice(TRADE_TYPES)
        resource_offered = resource_offered or random.choice(RESOURCE_TYPES)
        resource_requested = resource_requested or random.choice(RESOURCE_TYPES)
        amount = round(random.uniform(10, 500), 1)
        price = round(random.uniform(5, 200), 1)

        trade_id = await db.create_trade_agreement(
            civilization_a_id=civ_a_id, civilization_b_id=civ_b_id,
            trade_type=trade_type, resource_offered=resource_offered,
            resource_requested=resource_requested,
            amount_offered=amount, amount_requested=amount * random.uniform(0.5, 1.5),
            price=price, duration_days=random.randint(10, 90),
        )
        self.stats["agreements_created"] += 1

        rel = await db.get_diplomatic_relation(civ_a_id, civ_b_id)
        if rel:
            await db.update_diplomatic_relation(
                rel["id"],
                trade_volume=rel.get("trade_volume", 0) + price,
                agreements_count=rel.get("agreements_count", 0) + 1,
            )

        await db.record_history(civ_a_id, "trade_started",
                                f"Trade agreement: {trade_type} ({resource_offered} for {resource_requested})",
                                impact_score=price / 10,
                                related_civilization_id=civ_b_id)
        await dispatch(Event(EventType.TRADE_STARTED, {
            "trade_id": trade_id, "civilization_a_id": civ_a_id,
            "civilization_b_id": civ_b_id, "trade_type": trade_type,
        }))
        return {"trade_id": trade_id, "trade_type": trade_type,
                "amount": amount, "price": price}

    async def tick_trades(self) -> dict:
        trades = await db.list_trade_agreements(status="active")
        completed = 0
        for t in trades:
            new_days = t.get("days_elapsed", 0) + 1
            if new_days >= t.get("duration", 30):
                await db.update_trade_agreement(t["id"], status="completed")
                self.stats["total_volume"] += t.get("total_volume", 0) + t.get("price", 0)
                completed += 1
            else:
                vol = t.get("price", 0) * random.uniform(0.8, 1.2)
                await db.update_trade_agreement(
                    t["id"], days_elapsed=new_days,
                    total_volume=t.get("total_volume", 0) + vol)
        return {"trades_ticked": len(trades), "completed": completed}

    async def list_trades(self, civ_id: str | None = None) -> list[dict]:
        return await db.list_trade_agreements(civ_id)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


trade_engine = TradeEngine()
