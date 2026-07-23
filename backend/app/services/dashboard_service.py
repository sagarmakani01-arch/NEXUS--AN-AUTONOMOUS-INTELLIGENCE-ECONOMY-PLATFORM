from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.schemas.dashboard import DashboardStats
from app.repositories.agent_repo import AgentRepository
from app.repositories.company_repo import CompanyRepository
from app.repositories.task_repo import TaskRepository
from app.repositories.transaction_repo import TransactionRepository
from app.repositories.user_repo import UserRepository


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_stats(self) -> DashboardStats:
        agent_repo = AgentRepository(self.session)
        task_repo = TaskRepository(self.session)
        user_repo = UserRepository(self.session)
        company_repo = CompanyRepository(self.session)
        tx_repo = TransactionRepository(self.session)

        total_agents = await agent_repo.count()
        active_agents = await agent_repo.get_active_agents()
        total_users = await user_repo.count()
        total_companies = await company_repo.count()
        total_transactions = await tx_repo.count()

        from sqlalchemy import func, select
        from app.domain.models.task import Task

        result = await self.session.execute(
            select(func.count()).select_from(Task).where(Task.status.in_(["open", "in_progress"]))
        )
        active_tasks = result.scalar_one()

        return DashboardStats(
            total_agents=total_agents,
            active_agents=active_agents,
            active_tasks=active_tasks,
            total_users=total_users,
            total_companies=total_companies,
            total_transactions=total_transactions,
        )
