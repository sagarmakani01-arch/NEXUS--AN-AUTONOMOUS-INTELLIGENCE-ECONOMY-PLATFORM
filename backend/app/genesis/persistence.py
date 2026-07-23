import json
from typing import Optional

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.genesis import (
    GenesisCivilization, GenesisAgent, BeliefSystem, Philosophy,
    CreatorInteraction, HistoricalInterpretation, GenesisDiscovery,
    EraRecord, KnowledgeDomain, CreatorAwarenessRecord,
)


class GenesisDB:
    # ── Civilization ──

    @staticmethod
    async def create_civilization(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = GenesisCivilization(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _civ_to_dict(obj)

    @staticmethod
    async def get_civilization(civ_id: str) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(GenesisCivilization).where(GenesisCivilization.id == civ_id))
            o = r.scalar_one_or_none()
            return _civ_to_dict(o) if o else None

    @staticmethod
    async def update_civilization(civ_id: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(GenesisCivilization).where(GenesisCivilization.id == civ_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _civ_to_dict(o)

    @staticmethod
    async def list_civilizations() -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(GenesisCivilization).order_by(GenesisCivilization.created_at.desc()))
            return [_civ_to_dict(o) for o in r.scalars().all()]

    # ── Agents ──

    @staticmethod
    async def create_agent(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = GenesisAgent(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _agent_to_dict(obj)

    @staticmethod
    async def get_agents(civ_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(GenesisAgent).where(GenesisAgent.civilization_id == civ_id))
            return [_agent_to_dict(o) for o in r.scalars().all()]

    @staticmethod
    async def update_agent(agent_id: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(GenesisAgent).where(GenesisAgent.id == agent_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _agent_to_dict(o)

    # ── Belief Systems ──

    @staticmethod
    async def create_belief(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = BeliefSystem(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _belief_to_dict(obj)

    @staticmethod
    async def get_beliefs(civ_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(BeliefSystem).where(BeliefSystem.civilization_id == civ_id))
            return [_belief_to_dict(o) for o in r.scalars().all()]

    @staticmethod
    async def update_belief(belief_id: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(BeliefSystem).where(BeliefSystem.id == belief_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _belief_to_dict(o)

    # ── Philosophies ──

    @staticmethod
    async def update_philosophy(phil_id: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(Philosophy).where(Philosophy.id == phil_id))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _phil_to_dict(o)

    @staticmethod
    async def create_philosophy(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = Philosophy(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _phil_to_dict(obj)

    @staticmethod
    async def get_philosophies(civ_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(Philosophy).where(Philosophy.civilization_id == civ_id))
            return [_phil_to_dict(o) for o in r.scalars().all()]

    # ── Creator Interactions ──

    @staticmethod
    async def create_interaction(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = CreatorInteraction(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _interaction_to_dict(obj)

    @staticmethod
    async def get_interactions(civ_id: str, limit: int = 50) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(CreatorInteraction).where(CreatorInteraction.civilization_id == civ_id)
                .order_by(CreatorInteraction.created_at.desc()).limit(limit))
            return [_interaction_to_dict(o) for o in r.scalars().all()]

    # ── Historical Interpretations ──

    @staticmethod
    async def create_interpretation(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = HistoricalInterpretation(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _interp_to_dict(obj)

    @staticmethod
    async def get_interpretations(civ_id: str, limit: int = 50) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(HistoricalInterpretation).where(HistoricalInterpretation.civilization_id == civ_id)
                .order_by(HistoricalInterpretation.created_at.desc()).limit(limit))
            return [_interp_to_dict(o) for o in r.scalars().all()]

    # ── Discoveries ──

    @staticmethod
    async def create_discovery(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = GenesisDiscovery(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _discovery_to_dict(obj)

    @staticmethod
    async def get_discoveries(civ_id: str, limit: int = 50) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(GenesisDiscovery).where(GenesisDiscovery.civilization_id == civ_id)
                .order_by(GenesisDiscovery.created_at.desc()).limit(limit))
            return [_discovery_to_dict(o) for o in r.scalars().all()]

    # ── Era Records ──

    @staticmethod
    async def create_era(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = EraRecord(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _era_to_dict(obj)

    @staticmethod
    async def get_eras(civ_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(EraRecord).where(EraRecord.civilization_id == civ_id)
                .order_by(EraRecord.start_year.asc()))
            return [_era_to_dict(o) for o in r.scalars().all()]

    @staticmethod
    async def close_era(civ_id: str, era_name: str, end_year: int) -> None:
        async with async_session_factory() as s:
            r = await s.execute(
                select(EraRecord).where(and_(
                    EraRecord.civilization_id == civ_id,
                    EraRecord.era_name == era_name,
                )))
            o = r.scalar_one_or_none()
            if o:
                o.end_year = end_year
                await s.commit()

    # ── Knowledge Domains ──

    @staticmethod
    async def get_or_create_knowledge(civ_id: str, domain_name: str) -> dict:
        async with async_session_factory() as s:
            r = await s.execute(select(KnowledgeDomain).where(and_(
                KnowledgeDomain.civilization_id == civ_id,
                KnowledgeDomain.domain_name == domain_name,
            )))
            o = r.scalar_one_or_none()
            if o:
                return _knowledge_to_dict(o)
            obj = KnowledgeDomain(civilization_id=civ_id, domain_name=domain_name)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _knowledge_to_dict(obj)

    @staticmethod
    async def update_knowledge(civ_id: str, domain_name: str, **kwargs) -> Optional[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(KnowledgeDomain).where(and_(
                KnowledgeDomain.civilization_id == civ_id,
                KnowledgeDomain.domain_name == domain_name,
            )))
            o = r.scalar_one_or_none()
            if not o:
                return None
            for k, v in kwargs.items():
                if hasattr(o, k):
                    setattr(o, k, v)
            await s.commit()
            await s.refresh(o)
            return _knowledge_to_dict(o)

    @staticmethod
    async def get_knowledge_domains(civ_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(select(KnowledgeDomain).where(KnowledgeDomain.civilization_id == civ_id))
            return [_knowledge_to_dict(o) for o in r.scalars().all()]

    # ── Creator Awareness ──

    @staticmethod
    async def create_awareness_record(**kwargs) -> dict:
        async with async_session_factory() as s:
            obj = CreatorAwarenessRecord(**kwargs)
            s.add(obj)
            await s.commit()
            await s.refresh(obj)
            return _awareness_to_dict(obj)

    @staticmethod
    async def get_awareness_records(civ_id: str) -> list[dict]:
        async with async_session_factory() as s:
            r = await s.execute(
                select(CreatorAwarenessRecord).where(CreatorAwarenessRecord.civilization_id == civ_id)
                .order_by(CreatorAwarenessRecord.recorded_at.desc()))
            return [_awareness_to_dict(o) for o in r.scalars().all()]

    # ── Stats ──

    @staticmethod
    async def get_belief_stats(civ_id: str) -> dict:
        async with async_session_factory() as s:
            r = await s.execute(select(func.count(BeliefSystem.id)).where(BeliefSystem.civilization_id == civ_id))
            total = r.scalar() or 0
            r2 = await s.execute(select(func.count(Philosophy.id)).where(Philosophy.civilization_id == civ_id))
            philosophies = r2.scalar() or 0
            r3 = await s.execute(select(func.count(GenesisDiscovery.id)).where(GenesisDiscovery.civilization_id == civ_id))
            discoveries = r3.scalar() or 0
            return {"beliefs": total, "philosophies": philosophies, "discoveries": discoveries}


genesis_db = GenesisDB()


def _civ_to_dict(o: GenesisCivilization) -> dict:
    return {
        "id": o.id, "name": o.name, "population": o.population,
        "era": o.era, "creation_year": o.creation_year, "current_year": o.current_year,
        "technology_level": o.technology_level, "culture_level": o.culture_level,
        "scientific_level": o.scientific_level, "awareness_level": o.awareness_level,
        "has_discovered_simulation": bool(o.has_discovered_simulation),
        "origin_story": o.origin_story,
        "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _agent_to_dict(o: GenesisAgent) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id, "name": o.name,
        "role": o.role, "status": o.status,
        "intelligence_level": o.intelligence_level, "survival_skill": o.survival_skill,
        "learning_rate": o.learning_rate, "social_influence": o.social_influence,
        "knowledge_areas": json.loads(o.knowledge_areas) if o.knowledge_areas else [],
        "energy": o.energy, "discovery_count": o.discovery_count,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _belief_to_dict(o: BeliefSystem) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id, "name": o.name,
        "belief_type": o.belief_type, "origin_explanation": o.origin_explanation,
        "natural_event_explanations": json.loads(o.natural_event_explanations) if o.natural_event_explanations else {},
        "creator_concept": o.creator_concept,
        "core_tenets": json.loads(o.core_tenets) if o.core_tenets else [],
        "rituals": json.loads(o.rituals) if o.rituals else [],
        "followers_count": o.followers_count, "influence_level": o.influence_level,
        "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _phil_to_dict(o: Philosophy) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id, "name": o.name,
        "philosopher_agent_id": o.philosopher_agent_id,
        "school_of_thought": o.school_of_thought,
        "core_ideas": json.loads(o.core_ideas) if o.core_ideas else [],
        "influence": o.influence, "followers": o.followers, "status": o.status,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _interaction_to_dict(o: CreatorInteraction) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "interaction_type": o.interaction_type, "description": o.description,
        "civilization_interpretation": o.civilization_interpretation,
        "impact_level": o.impact_level,
        "belief_impact": json.loads(o.belief_impact) if o.belief_impact else {},
        "triggered_by_creator": bool(o.triggered_by_creator),
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _interp_to_dict(o: HistoricalInterpretation) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "event_type": o.event_type, "actual_event": o.actual_event,
        "civilization_interpretation": o.civilization_interpretation,
        "impact_on_beliefs": json.loads(o.impact_on_beliefs) if o.impact_on_beliefs else {},
        "recorded_by_agent_id": o.recorded_by_agent_id,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _discovery_to_dict(o: GenesisDiscovery) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "discovery_type": o.discovery_type, "title": o.title,
        "description": o.description, "discoverer_agent_id": o.discoverer_agent_id,
        "impact_level": o.impact_level, "era_recorded": o.era_recorded,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _era_to_dict(o: EraRecord) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id, "era_name": o.era_name,
        "start_year": o.start_year, "end_year": o.end_year,
        "key_events": json.loads(o.key_events) if o.key_events else [],
        "population_at_start": o.population_at_start,
        "technology_level": o.technology_level, "culture_level": o.culture_level,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _knowledge_to_dict(o: KnowledgeDomain) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "domain_name": o.domain_name, "level": o.level,
        "understanding": o.understanding, "discoveries_made": o.discoveries_made,
        "created_at": o.created_at.isoformat() if o.created_at else None,
    }


def _awareness_to_dict(o: CreatorAwarenessRecord) -> dict:
    return {
        "id": o.id, "civilization_id": o.civilization_id,
        "awareness_level": o.awareness_level,
        "understanding_description": o.understanding_description,
        "evidence_collected": json.loads(o.evidence_collected) if o.evidence_collected else [],
        "philosopher_responsible": o.philosopher_responsible,
        "recorded_at": o.recorded_at.isoformat() if o.recorded_at else None,
    }
