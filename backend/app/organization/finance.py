from __future__ import annotations

import logging
import random

from app.organization import persistence as op

logger = logging.getLogger("nexus.organization.finance")


class CompanyFinanceManager:
    async def deposit(self, company_id: str, amount: float, category: str = "investment", description: str = "") -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}
        new_balance = company["treasury_balance"] + amount
        await op.update_company(company_id, treasury_balance=new_balance)
        await op.record_finance(
            company_id, "revenue", amount, category, description,
            balance_after=new_balance,
        )
        await op.add_memory(company_id, "revenue", f"Deposited {amount:.0f} NXC", description or category, "medium")
        return {"balance": new_balance, "amount": amount}

    async def withdraw(self, company_id: str, amount: float, category: str = "expense", description: str = "") -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}
        if company["treasury_balance"] < amount:
            return {"error": "Insufficient funds", "balance": company["treasury_balance"], "required": amount}
        new_balance = company["treasury_balance"] - amount
        await op.update_company(company_id, treasury_balance=new_balance, expenses=company["expenses"] + amount)
        await op.record_finance(
            company_id, "expense", amount, category, description,
            balance_after=new_balance,
        )
        return {"balance": new_balance, "amount": amount}

    async def pay_salary(self, company_id: str, agent_id: str, amount: float) -> dict:
        result = await self.withdraw(company_id, amount, "salary", f"Salary for agent {agent_id}")
        if "error" in result:
            return result
        await op.add_memory(company_id, "salary_paid", f"Paid {amount:.0f} NXC to agent {agent_id}", "", "low")
        return result

    async def process_payroll(self, company_id: str) -> dict:
        members = await op.get_members(company_id)
        total_paid = 0
        paid_count = 0
        failed_count = 0
        for member in members:
            if member["salary"] > 0:
                result = await self.pay_salary(company_id, member["agent_id"], member["salary"])
                if "error" not in result:
                    total_paid += member["salary"]
                    paid_count += 1
                else:
                    failed_count += 1
        return {
            "total_paid": round(total_paid, 2),
            "employees_paid": paid_count,
            "failed_payments": failed_count,
        }

    async def generate_revenue(self, company_id: str, amount: float, source: str = "product") -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}
        new_revenue = company["revenue"] + amount
        new_balance = company["treasury_balance"] + amount
        await op.update_company(company_id, revenue=new_revenue, treasury_balance=new_balance)
        await op.record_finance(
            company_id, "revenue", amount, source,
            f"Revenue from {source}",
            balance_after=new_balance,
        )
        return {"revenue": new_revenue, "balance": new_balance, "amount": amount}

    async def get_financial_report(self, company_id: str) -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}
        finances = await op.get_finances(company_id)
        revenue_txns = [f for f in finances if f["transaction_type"] == "revenue"]
        expense_txns = [f for f in finances if f["transaction_type"] == "expense"]
        salary_txns = [f for f in finances if f["category"] == "salary"]
        return {
            "company_id": company_id,
            "treasury_balance": company["treasury_balance"],
            "total_revenue": company["revenue"],
            "total_expenses": company["expenses"],
            "profit_loss": company["revenue"] - company["expenses"],
            "salary_expenses": sum(f["amount"] for f in salary_txns),
            "transaction_count": len(finances),
            "revenue_transactions": len(revenue_txns),
            "expense_transactions": len(expense_txns),
        }

    async def get_company_health(self, company_id: str) -> dict:
        company = await op.get_company(company_id)
        if not company:
            return {"error": "Company not found"}
        balance = company["treasury_balance"]
        revenue = company["revenue"]
        expenses = company["expenses"]
        employees = company["employee_count"]
        reputation = company["reputation"]
        if balance > 500 and revenue > expenses:
            health = "excellent"
        elif balance > 200 and revenue >= expenses * 0.8:
            health = "good"
        elif balance > 50:
            health = "fair"
        elif balance > 0:
            health = "poor"
        else:
            health = "critical"
        return {
            "company_id": company_id,
            "health": health,
            "balance": balance,
            "revenue": revenue,
            "expenses": expenses,
            "profit_margin": round((revenue - expenses) / max(revenue, 1) * 100, 1),
            "employees": employees,
            "reputation": reputation,
        }


finance_manager = CompanyFinanceManager()
