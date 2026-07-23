import logging
from datetime import datetime, timezone, timedelta

from app.economy import persistence as eco_db
from app.resources.persistence import get_wallet, update_balance, create_transaction
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.economy.finance")

BANK_ID = "nexus_central_bank"


class FinanceEngine:
    def __init__(self):
        self.base_interest_rate = 0.05
        self.savings_rate = 0.02
        self.inflation_rate = 0.02
        self.money_supply = 0.0
        self.stats = {
            "loans_issued": 0,
            "loans_repaid": 0,
            "interest_earned": 0,
            "total_deposits": 0,
        }

    async def issue_loan(self, borrower_id: str, borrower_type: str, amount: float,
                         term_days: int = 30) -> dict:
        wallet = await get_wallet(borrower_id)
        if not wallet:
            return {"success": False, "error": "No wallet found"}

        credit_score = min(100, max(0, wallet.get("total_earned", 0) / 10))
        interest_rate = self.base_interest_rate * (1.5 - credit_score / 100)

        loan_id = await eco_db.create_loan(
            borrower_id=borrower_id,
            borrower_type=borrower_type,
            amount=amount,
            interest_rate=round(interest_rate, 4),
            term_days=term_days,
            lender_id=BANK_ID,
        )

        await update_balance(borrower_id, amount)
        await create_transaction(
            from_wallet_id=BANK_ID, to_wallet_id=borrower_id,
            amount=amount, transaction_type="loan",
            notes=f"Loan issued: {amount} NXC at {interest_rate:.2%} for {term_days} days",
        )

        self.stats["loans_issued"] += 1
        self.money_supply += amount

        await dispatch(Event(EventType.LOAN_ISSUED, {
            "loan_id": loan_id, "borrower_id": borrower_id,
            "amount": amount, "interest_rate": interest_rate,
        }))

        return {
            "success": True,
            "loan_id": loan_id,
            "amount": amount,
            "interest_rate": interest_rate,
            "term_days": term_days,
        }

    async def repay_loan(self, loan_id: str, amount: float) -> dict:
        loans = await eco_db.get_loans(loan_id)
        if not loans:
            return {"success": False, "error": "Loan not found"}
        loan = loans[0]

        if loan["status"] != "active":
            return {"success": False, "error": "Loan not active"}

        wallet = await get_wallet(loan["borrower_id"])
        if not wallet or wallet.get("balance", 0) < amount:
            return {"success": False, "error": "Insufficient funds"}

        await update_balance(loan["borrower_id"], -amount)
        total_paid = loan["amount_paid"] + amount

        if total_paid >= loan["amount"] * (1 + loan["interest_rate"]):
            await eco_db.update_loan(loan_id, amount_paid=total_paid, status="completed",
                                     completed_at=datetime.now(timezone.utc))
            self.stats["loans_repaid"] += 1
        else:
            await eco_db.update_loan(loan_id, amount_paid=total_paid)

        interest = max(0, total_paid - loan["amount"])
        self.stats["interest_earned"] += interest

        await create_transaction(
            from_wallet_id=loan["borrower_id"], to_wallet_id=BANK_ID,
            amount=amount, transaction_type="loan_repayment",
            notes=f"Loan repayment for {loan_id}",
        )

        return {
            "success": True,
            "amount_paid": total_paid,
            "remaining": max(0, loan["amount"] * (1 + loan["interest_rate"]) - total_paid),
        }

    async def process_savings(self, agent_id: str, amount: float) -> dict:
        wallet = await get_wallet(agent_id)
        if not wallet or wallet.get("balance", 0) < amount:
            return {"success": False, "error": "Insufficient funds"}

        await update_balance(agent_id, -amount)
        interest = amount * self.savings_rate
        await update_balance(agent_id, interest)

        await create_transaction(
            from_wallet_id=agent_id, to_wallet_id=BANK_ID,
            amount=amount, transaction_type="savings_deposit",
            notes=f"Savings deposit: {amount} NXC at {self.savings_rate:.2%}",
        )

        self.stats["total_deposits"] += amount
        return {
            "success": True,
            "deposited": amount,
            "interest_earned": round(interest, 2),
            "savings_rate": self.savings_rate,
        }

    async def process_daily_interest(self, agent_ids: list[str]) -> None:
        for agent_id in agent_ids:
            wallet = await get_wallet(agent_id)
            if wallet and wallet.get("balance", 0) > 0:
                daily_interest = wallet["balance"] * self.savings_rate / 365
                if daily_interest > 0.01:
                    await update_balance(agent_id, daily_interest)

    def update_rates(self, economic_conditions: float) -> None:
        if economic_conditions > 1.2:
            self.base_interest_rate = min(0.15, self.base_interest_rate + 0.005)
            self.savings_rate = min(0.05, self.savings_rate + 0.002)
        elif economic_conditions < 0.8:
            self.base_interest_rate = max(0.02, self.base_interest_rate - 0.005)
            self.savings_rate = max(0.005, self.savings_rate - 0.001)

    async def get_financial_overview(self) -> dict:
        return {
            "bank_id": BANK_ID,
            "base_interest_rate": self.base_interest_rate,
            "savings_rate": self.savings_rate,
            "inflation_rate": self.inflation_rate,
            "money_supply": round(self.money_supply, 2),
            "stats": self.stats.copy(),
        }

    def get_state(self) -> dict:
        return {
            "base_interest_rate": self.base_interest_rate,
            "savings_rate": self.savings_rate,
            "inflation_rate": self.inflation_rate,
            "money_supply": round(self.money_supply, 2),
            "stats": self.stats.copy(),
        }


finance_engine = FinanceEngine()
