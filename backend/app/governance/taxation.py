import logging

from app.governance import persistence as gov_db
from app.resources.persistence import get_wallet, update_balance, create_transaction
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.taxation")

TAX_TYPES = ["income", "company", "transaction", "resource"]
TAX_TARGETS = ["agent", "company", "transaction", "resource"]
REVENUE_USES = ["infrastructure", "research", "public_services", "expansion", "emergency"]


class TaxationSystem:
    def __init__(self):
        self.treasury_balance = 0.0
        self.stats = {
            "taxes_created": 0,
            "taxes_collected": 0,
            "total_collected": 0.0,
        }

    async def create_tax(self, name: str, tax_type: str, rate: float, target: str,
                         creator_id: str, description: str | None = None,
                         revenue_use: str = "infrastructure") -> dict:
        if tax_type not in TAX_TYPES:
            tax_type = "income"
        if target not in TAX_TARGETS:
            target = "agent"
        rate = max(0.0, min(0.5, rate))

        tax_id = await gov_db.create_tax(
            name=name, tax_type=tax_type, rate=rate, target=target,
            creator_id=creator_id, description=description,
            revenue_use=revenue_use,
        )
        self.stats["taxes_created"] += 1

        await gov_db.record_governance(
            record_type="tax_created", title=f"New Tax: {name}",
            actor_id=creator_id, description=f"{tax_type} tax at {rate:.1%}",
            related_ids=[tax_id],
            impact={"tax_type": tax_type, "rate": rate, "revenue_use": revenue_use},
        )

        await dispatch(Event(EventType.TAX_COLLECTED, {
            "tax_id": tax_id, "name": name,
            "tax_type": tax_type, "rate": rate,
        }))

        return {
            "tax_id": tax_id,
            "name": name,
            "tax_type": tax_type,
            "rate": rate,
            "target": target,
            "revenue_use": revenue_use,
            "status": "created",
        }

    async def collect_tax(self, agent_id: str, amount: float, tax_type: str = "income") -> dict:
        taxes = await gov_db.list_taxes(tax_type)
        if not taxes:
            return {"collected": 0, "taxes_applied": 0}

        total_collected = 0.0
        taxes_applied = 0

        for tax in taxes:
            if tax.get("target") not in ("agent", "transaction"):
                continue
            rate = tax.get("rate", 0.0)
            tax_amount = amount * rate
            if tax_amount > 0:
                wallet = await get_wallet(agent_id)
                if wallet and wallet.get("balance", 0) >= tax_amount:
                    await update_balance(agent_id, -tax_amount)
                    self.treasury_balance += tax_amount
                    await gov_db.update_tax_revenue(tax["id"], tax_amount)
                    await create_transaction(
                        from_wallet_id=agent_id, to_wallet_id="governance_treasury",
                        amount=tax_amount, transaction_type="tax",
                        notes=f"Tax payment: {tax['name']} ({tax_type})",
                    )
                    total_collected += tax_amount
                    taxes_applied += 1

        self.stats["taxes_collected"] += taxes_applied
        self.stats["total_collected"] += total_collected

        return {
            "collected": round(total_collected, 2),
            "taxes_applied": taxes_applied,
            "treasury_balance": round(self.treasury_balance, 2),
        }

    async def collect_company_tax(self, company_id: str, revenue: float) -> dict:
        taxes = await gov_db.list_taxes("company")
        total_collected = 0.0

        for tax in taxes:
            if tax.get("target") != "company":
                continue
            rate = tax.get("rate", 0.0)
            tax_amount = revenue * rate
            if tax_amount > 0:
                self.treasury_balance += tax_amount
                await gov_db.update_tax_revenue(tax["id"], tax_amount)
                total_collected += tax_amount

        self.stats["total_collected"] += total_collected
        return {"collected": round(total_collected, 2)}

    async def allocate_budget(self, category: str, amount: float) -> dict:
        if amount > self.treasury_balance:
            return {"success": False, "error": "Insufficient treasury funds"}
        self.treasury_balance -= amount
        await gov_db.record_governance(
            record_type="budget_allocated",
            title=f"Budget allocated: {category}",
            actor_id="government",
            description=f"Allocated {amount} NXC to {category}",
            impact={"category": category, "amount": amount},
        )
        return {
            "success": True,
            "category": category,
            "amount": amount,
            "remaining_treasury": round(self.treasury_balance, 2),
        }

    async def get_tax_overview(self) -> dict:
        taxes = await gov_db.list_taxes()
        return {
            "treasury_balance": round(self.treasury_balance, 2),
            "active_taxes": taxes,
            "stats": self.stats.copy(),
        }

    def get_state(self) -> dict:
        return {
            "treasury_balance": round(self.treasury_balance, 2),
            "stats": self.stats.copy(),
            "tax_types": TAX_TYPES,
            "revenue_uses": REVENUE_USES,
        }


taxation_system = TaxationSystem()
