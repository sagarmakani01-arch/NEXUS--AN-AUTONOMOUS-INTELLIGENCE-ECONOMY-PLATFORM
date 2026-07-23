import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.federation import (
    Civilization, CivilizationRules, DiplomaticRelation, TradeAgreement,
    FederationCouncil, Migration, CivilizationHistory, InterCivilizationMessage,
)

logger = logging.getLogger("nexus.federation.persistence")


async def create_civilization(**kwargs) -> str:
    async with async_session_factory() as session:
        c = Civilization(**kwargs)
        session.add(c)
        await session.commit()
        return c.id


async def get_civilization(civ_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(Civilization).where(Civilization.id == civ_id))
        c = r.scalar_one_or_none()
        return _civ_to_dict(c) if c else None


async def list_civilizations(status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Civilization).where(Civilization.status == status)
        stmt = stmt.order_by(Civilization.economic_power.desc())
        r = await session.execute(stmt)
        return [_civ_to_dict(c) for c in r.scalars().all()]


async def update_civilization(civ_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(Civilization).where(Civilization.id == civ_id))
        c = r.scalar_one_or_none()
        if c:
            for k, v in kwargs.items():
                if hasattr(c, k):
                    setattr(c, k, v)
            c.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_rules(civilization_id: str, **kwargs) -> str:
    async with async_session_factory() as session:
        rules = CivilizationRules(civilization_id=civilization_id, **kwargs)
        session.add(rules)
        await session.commit()
        return rules.id


async def get_rules(civilization_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationRules).where(
            CivilizationRules.civilization_id == civilization_id))
        rules = r.scalar_one_or_none()
        if not rules:
            return None
        return {
            "id": rules.id, "civilization_id": rules.civilization_id,
            "economic_model": rules.economic_model, "governance_type": rules.governance_type,
            "resource_availability": rules.resource_availability,
            "migration_policy": rules.migration_policy, "trade_policy": rules.trade_policy,
            "research_policy": rules.research_policy, "defense_policy": rules.defense_policy,
            "custom_rules": json.loads(rules.custom_rules) if rules.custom_rules else {},
        }


async def update_rules(civilization_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(CivilizationRules).where(
            CivilizationRules.civilization_id == civilization_id))
        rules = r.scalar_one_or_none()
        if rules:
            for k, v in kwargs.items():
                if hasattr(rules, k):
                    setattr(rules, k, v)
            rules.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_diplomatic_relation(civ_a_id: str, civ_b_id: str, **kwargs) -> str:
    async with async_session_factory() as session:
        rel = DiplomaticRelation(civilization_a_id=civ_a_id, civilization_b_id=civ_b_id, **kwargs)
        session.add(rel)
        await session.commit()
        return rel.id


async def get_diplomatic_relation(civ_a_id: str, civ_b_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(DiplomaticRelation).where(
            and_(DiplomaticRelation.civilization_a_id == civ_a_id,
                 DiplomaticRelation.civilization_b_id == civ_b_id)))
        rel = r.scalar_one_or_none()
        if not rel:
            r2 = await session.execute(select(DiplomaticRelation).where(
                and_(DiplomaticRelation.civilization_a_id == civ_b_id,
                     DiplomaticRelation.civilization_b_id == civ_a_id)))
            rel = r2.scalar_one_or_none()
        if not rel:
            return None
        return {
            "id": rel.id, "civilization_a_id": rel.civilization_a_id,
            "civilization_b_id": rel.civilization_b_id,
            "relation_level": rel.relation_level, "status": rel.status,
            "trust_score": rel.trust_score, "trade_volume": rel.trade_volume,
            "agreements_count": rel.agreements_count, "conflicts_count": rel.conflicts_count,
            "created_at": rel.created_at.isoformat() if rel.created_at else None,
        }


async def list_diplomatic_relations(civ_id: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(DiplomaticRelation)
        if civ_id:
            stmt = stmt.where(
                (DiplomaticRelation.civilization_a_id == civ_id) |
                (DiplomaticRelation.civilization_b_id == civ_id))
        r = await session.execute(stmt)
        return [
            {"id": rel.id, "civilization_a_id": rel.civilization_a_id,
             "civilization_b_id": rel.civilization_b_id,
             "relation_level": rel.relation_level, "status": rel.status,
             "trust_score": rel.trust_score}
            for rel in r.scalars().all()
        ]


async def update_diplomatic_relation(rel_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(DiplomaticRelation).where(DiplomaticRelation.id == rel_id))
        rel = r.scalar_one_or_none()
        if rel:
            for k, v in kwargs.items():
                if hasattr(rel, k):
                    setattr(rel, k, v)
            rel.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_trade_agreement(**kwargs) -> str:
    async with async_session_factory() as session:
        t = TradeAgreement(**kwargs)
        session.add(t)
        await session.commit()
        return t.id


async def list_trade_agreements(civ_id: str | None = None, status: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(TradeAgreement)
        conds = []
        if civ_id:
            conds.append((TradeAgreement.civilization_a_id == civ_id) |
                         (TradeAgreement.civilization_b_id == civ_id))
        if status:
            conds.append(TradeAgreement.status == status)
        if conds:
            stmt = stmt.where(and_(*conds))
        r = await session.execute(stmt)
        return [
            {"id": t.id, "civilization_a_id": t.civilization_a_id,
             "civilization_b_id": t.civilization_b_id,
             "trade_type": t.trade_type, "resource_offered": t.resource_offered,
             "resource_requested": t.resource_requested,
             "amount_offered": t.amount_offered, "amount_requested": t.amount_requested,
             "price": t.price, "total_volume": t.total_volume, "status": t.status,
             "created_at": t.created_at.isoformat() if t.created_at else None}
            for t in r.scalars().all()
        ]


async def update_trade_agreement(trade_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        r = await session.execute(select(TradeAgreement).where(TradeAgreement.id == trade_id))
        t = r.scalar_one_or_none()
        if t:
            for k, v in kwargs.items():
                if hasattr(t, k):
                    setattr(t, k, v)
            t.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_federation_council(**kwargs) -> str:
    async with async_session_factory() as session:
        fc = FederationCouncil(**kwargs)
        session.add(fc)
        await session.commit()
        return fc.id


async def get_federation_council(council_id: str) -> dict | None:
    async with async_session_factory() as session:
        r = await session.execute(select(FederationCouncil).where(FederationCouncil.id == council_id))
        fc = r.scalar_one_or_none()
        if not fc:
            return None
        return {
            "id": fc.id, "name": fc.name, "description": fc.description,
            "member_civilization_ids": json.loads(fc.member_civilization_ids) if fc.member_civilization_ids else [],
            "founding_civilization_id": fc.founding_civilization_id,
            "rules": json.loads(fc.rules) if fc.rules else {},
            "resolution_count": fc.resolution_count, "status": fc.status,
            "created_at": fc.created_at.isoformat() if fc.created_at else None,
        }


async def list_federation_councils() -> list[dict]:
    async with async_session_factory() as session:
        r = await session.execute(select(FederationCouncil).where(FederationCouncil.status == "active"))
        return [
            {"id": fc.id, "name": fc.name, "member_count": len(json.loads(fc.member_civilization_ids) if fc.member_civilization_ids else [])}
            for fc in r.scalars().all()
        ]


async def create_migration(**kwargs) -> str:
    async with async_session_factory() as session:
        m = Migration(**kwargs)
        session.add(m)
        await session.commit()
        return m.id


async def list_migrations(civ_id: str | None = None, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Migration)
        if civ_id:
            stmt = stmt.where(
                (Migration.origin_civilization_id == civ_id) |
                (Migration.destination_civilization_id == civ_id))
        stmt = stmt.order_by(Migration.migrated_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": m.id, "agent_id": m.agent_id,
             "origin_civilization_id": m.origin_civilization_id,
             "destination_civilization_id": m.destination_civilization_id,
             "reason": m.reason, "skill_value": m.skill_value,
             "status": m.status, "migrated_at": m.migrated_at.isoformat() if m.migrated_at else None}
            for m in r.scalars().all()
        ]


async def record_history(civilization_id: str, event_type: str, title: str,
                          description: str | None = None, impact_score: float = 0,
                          related_civilization_id: str | None = None) -> str:
    async with async_session_factory() as session:
        h = CivilizationHistory(
            civilization_id=civilization_id, event_type=event_type,
            title=title, description=description, impact_score=impact_score,
            related_civilization_id=related_civilization_id,
        )
        session.add(h)
        await session.commit()
        return h.id


async def get_history(civilization_id: str, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        r = await session.execute(
            select(CivilizationHistory)
            .where(CivilizationHistory.civilization_id == civilization_id)
            .order_by(CivilizationHistory.recorded_at.desc())
            .limit(limit))
        return [
            {"id": h.id, "event_type": h.event_type, "title": h.title,
             "description": h.description, "impact_score": h.impact_score,
             "recorded_at": h.recorded_at.isoformat() if h.recorded_at else None}
            for h in r.scalars().all()
        ]


async def create_message(**kwargs) -> str:
    async with async_session_factory() as session:
        m = InterCivilizationMessage(**kwargs)
        session.add(m)
        await session.commit()
        return m.id


async def list_messages(civ_id: str | None = None, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(InterCivilizationMessage)
        if civ_id:
            stmt = stmt.where(
                (InterCivilizationMessage.sender_civilization_id == civ_id) |
                (InterCivilizationMessage.receiver_civilization_id == civ_id))
        stmt = stmt.order_by(InterCivilizationMessage.created_at.desc()).limit(limit)
        r = await session.execute(stmt)
        return [
            {"id": m.id, "sender_civilization_id": m.sender_civilization_id,
             "receiver_civilization_id": m.receiver_civilization_id,
             "message_type": m.message_type, "subject": m.subject,
             "content": m.content, "status": m.status,
             "created_at": m.created_at.isoformat() if m.created_at else None}
            for m in r.scalars().all()
        ]


async def get_federation_stats() -> dict:
    async with async_session_factory() as session:
        civs = await session.execute(select(func.count(Civilization.id)))
        rels = await session.execute(select(func.count(DiplomaticRelation.id)))
        trades = await session.execute(select(func.count(TradeAgreement.id)))
        councils = await session.execute(select(func.count(FederationCouncil.id)))
        migrations = await session.execute(select(func.count(Migration.id)))
        return {
            "civilizations": civs.scalar() or 0,
            "diplomatic_relations": rels.scalar() or 0,
            "trade_agreements": trades.scalar() or 0,
            "federation_councils": councils.scalar() or 0,
            "migrations": migrations.scalar() or 0,
        }


def _civ_to_dict(c) -> dict:
    return {
        "id": c.id, "name": c.name, "description": c.description,
        "leader_agent_id": c.leader_agent_id,
        "population": c.population, "territory_size": c.territory_size,
        "technology_level": c.technology_level,
        "economic_power": c.economic_power, "military_strength": c.military_strength,
        "cultural_influence": c.cultural_influence, "research_output": c.research_output,
        "happiness": c.happiness, "resource_availability": c.resource_availability,
        "government_type": c.government_type, "economic_model": c.economic_model,
        "values": json.loads(c.values) if c.values else {},
        "priorities": json.loads(c.priorities) if c.priorities else [],
        "achievements": json.loads(c.achievements) if c.achievements else [],
        "reputation": c.reputation, "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }
