import json
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory as AsyncSessionLocal
from app.domain.models.meta import (
    UniverseObservation,
    CrossSimulationResult,
    DiscoveredPattern,
    RuleEvaluation,
    Experiment,
    Recommendation,
    KnowledgeEntry,
    SimulationReport,
)


class MetaPersistence:
    @staticmethod
    async def create_observation(obs: UniverseObservation) -> UniverseObservation:
        async with AsyncSessionLocal() as session:
            session.add(obs)
            await session.commit()
            await session.refresh(obs)
            return obs

    @staticmethod
    async def get_observations(simulation_id: str = None, limit: int = 200) -> list[UniverseObservation]:
        async with AsyncSessionLocal() as session:
            query = select(UniverseObservation)
            if simulation_id:
                query = query.where(UniverseObservation.simulation_id == simulation_id)
            query = query.order_by(UniverseObservation.tick.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def save_cross_result(result: CrossSimulationResult) -> CrossSimulationResult:
        async with AsyncSessionLocal() as session:
            session.add(result)
            await session.commit()
            await session.refresh(result)
            return result

    @staticmethod
    async def get_cross_results(limit: int = 100) -> list[CrossSimulationResult]:
        async with AsyncSessionLocal() as session:
            query = select(CrossSimulationResult).order_by(CrossSimulationResult.created_at.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def save_pattern(pattern: DiscoveredPattern) -> DiscoveredPattern:
        async with AsyncSessionLocal() as session:
            session.add(pattern)
            await session.commit()
            await session.refresh(pattern)
            return pattern

    @staticmethod
    async def get_patterns(pattern_type: str = None, status: str = None, limit: int = 100) -> list[DiscoveredPattern]:
        async with AsyncSessionLocal() as session:
            query = select(DiscoveredPattern)
            if pattern_type:
                query = query.where(DiscoveredPattern.pattern_type == pattern_type)
            if status:
                query = query.where(DiscoveredPattern.status == status)
            query = query.order_by(DiscoveredPattern.confidence.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def save_evaluation(eval: RuleEvaluation) -> RuleEvaluation:
        async with AsyncSessionLocal() as session:
            session.add(eval)
            await session.commit()
            await session.refresh(eval)
            return eval

    @staticmethod
    async def get_evaluations(rule_domain: str = None, limit: int = 100) -> list[RuleEvaluation]:
        async with AsyncSessionLocal() as session:
            query = select(RuleEvaluation)
            if rule_domain:
                query = query.where(RuleEvaluation.rule_domain == rule_domain)
            query = query.order_by(RuleEvaluation.effectiveness.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def create_experiment(exp: Experiment) -> Experiment:
        async with AsyncSessionLocal() as session:
            session.add(exp)
            await session.commit()
            await session.refresh(exp)
            return exp

    @staticmethod
    async def get_experiments(status: str = None, limit: int = 50) -> list[Experiment]:
        async with AsyncSessionLocal() as session:
            query = select(Experiment)
            if status:
                query = query.where(Experiment.status == status)
            query = query.order_by(Experiment.created_at.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def update_experiment(exp_id: str, **kwargs) -> Optional[Experiment]:
        async with AsyncSessionLocal() as session:
            exp = await session.get(Experiment, exp_id)
            if not exp:
                return None
            for key, value in kwargs.items():
                setattr(exp, key, value)
            await session.commit()
            await session.refresh(exp)
            return exp

    @staticmethod
    async def create_recommendation(rec: Recommendation) -> Recommendation:
        async with AsyncSessionLocal() as session:
            session.add(rec)
            await session.commit()
            await session.refresh(rec)
            return rec

    @staticmethod
    async def get_recommendations(status: str = None, limit: int = 50) -> list[Recommendation]:
        async with AsyncSessionLocal() as session:
            query = select(Recommendation)
            if status:
                query = query.where(Recommendation.status == status)
            query = query.order_by(Recommendation.confidence.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def update_recommendation(rec_id: str, **kwargs) -> Optional[Recommendation]:
        async with AsyncSessionLocal() as session:
            rec = await session.get(Recommendation, rec_id)
            if not rec:
                return None
            for key, value in kwargs.items():
                setattr(rec, key, value)
            await session.commit()
            await session.refresh(rec)
            return rec

    @staticmethod
    async def save_knowledge(entry: KnowledgeEntry) -> KnowledgeEntry:
        async with AsyncSessionLocal() as session:
            session.add(entry)
            await session.commit()
            await session.refresh(entry)
            return entry

    @staticmethod
    async def get_knowledge(entry_type: str = None, limit: int = 100) -> list[KnowledgeEntry]:
        async with AsyncSessionLocal() as session:
            query = select(KnowledgeEntry)
            if entry_type:
                query = query.where(KnowledgeEntry.entry_type == entry_type)
            query = query.order_by(KnowledgeEntry.confidence.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())

    @staticmethod
    async def save_report(report: SimulationReport) -> SimulationReport:
        async with AsyncSessionLocal() as session:
            session.add(report)
            await session.commit()
            await session.refresh(report)
            return report

    @staticmethod
    async def get_reports(report_type: str = None, limit: int = 50) -> list[SimulationReport]:
        async with AsyncSessionLocal() as session:
            query = select(SimulationReport)
            if report_type:
                query = query.where(SimulationReport.report_type == report_type)
            query = query.order_by(SimulationReport.generated_at.desc()).limit(limit)
            result = await session.execute(query)
            return list(result.scalars().all())


meta_persistence = MetaPersistence()
