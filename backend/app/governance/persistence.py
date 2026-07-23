import json
import logging
from datetime import datetime, timezone

from sqlalchemy import select, func, and_

from app.core.database import async_session_factory
from app.domain.models.governance import (
    GovernanceEntity, Law, Policy, Tax, Regulation, Conflict, Vote, GovernanceRecord,
)

logger = logging.getLogger("nexus.governance")


async def create_governance_entity(name: str, entity_type: str, description: str | None = None,
                                   authority_level: str = "individual",
                                   founder_id: str | None = None) -> str:
    async with async_session_factory() as session:
        entity = GovernanceEntity(
            name=name, entity_type=entity_type, description=description,
            authority_level=authority_level, founder_id=founder_id,
        )
        session.add(entity)
        await session.commit()
        return entity.id


async def get_governance_entity(entity_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(GovernanceEntity).where(GovernanceEntity.id == entity_id))
        e = result.scalar_one_or_none()
        if not e:
            return None
        return _entity_to_dict(e)


async def list_governance_entities(entity_type: str | None = None, authority_level: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(GovernanceEntity).where(GovernanceEntity.status == "active")
        if entity_type:
            stmt = stmt.where(GovernanceEntity.entity_type == entity_type)
        if authority_level:
            stmt = stmt.where(GovernanceEntity.authority_level == authority_level)
        result = await session.execute(stmt)
        return [_entity_to_dict(e) for e in result.scalars().all()]


async def update_governance_entity(entity_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(GovernanceEntity).where(GovernanceEntity.id == entity_id))
        e = result.scalar_one_or_none()
        if e:
            for k, v in kwargs.items():
                if hasattr(e, k):
                    setattr(e, k, v)
            e.updated_at = datetime.now(timezone.utc)
            await session.commit()


async def create_law(name: str, description: str | None, creator_id: str, scope: str = "global",
                     category: str = "general", severity: str = "medium",
                     affected_entities: list[str] | None = None, penalty: dict | None = None) -> str:
    async with async_session_factory() as session:
        law = Law(
            name=name, description=description, creator_id=creator_id,
            scope=scope, category=category, severity=severity,
            affected_entities=json.dumps(affected_entities or []),
            penalty=json.dumps(penalty or {}),
        )
        session.add(law)
        await session.commit()
        return law.id


async def get_law(law_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Law).where(Law.id == law_id))
        law = result.scalar_one_or_none()
        if not law:
            return None
        return _law_to_dict(law)


async def list_laws(category: str | None = None, status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Law).where(Law.status == status)
        if category:
            stmt = stmt.where(Law.category == category)
        result = await session.execute(stmt)
        return [_law_to_dict(l) for l in result.scalars().all()]


async def create_policy(name: str, description: str | None, policy_type: str,
                        creator_id: str, target: str | None = None,
                        rules: dict | None = None, expected_outcome: str | None = None,
                        duration_days: int = 30, priority: str = "medium") -> str:
    async with async_session_factory() as session:
        policy = Policy(
            name=name, description=description, policy_type=policy_type,
            creator_id=creator_id, target=target,
            rules=json.dumps(rules or {}),
            expected_outcome=expected_outcome,
            duration_days=duration_days, priority=priority,
        )
        session.add(policy)
        await session.commit()
        return policy.id


async def get_policy(policy_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Policy).where(Policy.id == policy_id))
        p = result.scalar_one_or_none()
        if not p:
            return None
        return _policy_to_dict(p)


async def list_policies(policy_type: str | None = None, status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Policy).where(Policy.status == status)
        if policy_type:
            stmt = stmt.where(Policy.policy_type == policy_type)
        result = await session.execute(stmt)
        return [_policy_to_dict(p) for p in result.scalars().all()]


async def update_policy(policy_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Policy).where(Policy.id == policy_id))
        p = result.scalar_one_or_none()
        if p:
            for k, v in kwargs.items():
                if hasattr(p, k):
                    setattr(p, k, v)
            await session.commit()


async def create_tax(name: str, tax_type: str, rate: float, target: str,
                     creator_id: str, description: str | None = None,
                     revenue_use: str = "infrastructure") -> str:
    async with async_session_factory() as session:
        tax = Tax(
            name=name, tax_type=tax_type, rate=rate, target=target,
            creator_id=creator_id, description=description,
            revenue_use=revenue_use,
        )
        session.add(tax)
        await session.commit()
        return tax.id


async def list_taxes(tax_type: str | None = None, status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Tax).where(Tax.status == status)
        if tax_type:
            stmt = stmt.where(Tax.tax_type == tax_type)
        result = await session.execute(stmt)
        return [
            {
                "id": t.id, "name": t.name, "tax_type": t.tax_type,
                "rate": t.rate, "target": t.target, "description": t.description,
                "revenue_total": t.revenue_total, "revenue_use": t.revenue_use,
                "status": t.status,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in result.scalars().all()
        ]


async def update_tax_revenue(tax_id: str, amount: float) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Tax).where(Tax.id == tax_id))
        tax = result.scalar_one_or_none()
        if tax:
            tax.revenue_total = (tax.revenue_total or 0) + amount
            await session.commit()


async def create_regulation(name: str, description: str | None, regulation_type: str,
                            authority_id: str, target_sector: str | None = None,
                            requirements: dict | None = None,
                            max_violations: int = 3,
                            penalty_description: str | None = None) -> str:
    async with async_session_factory() as session:
        reg = Regulation(
            name=name, description=description, regulation_type=regulation_type,
            authority_id=authority_id, target_sector=target_sector,
            requirements=json.dumps(requirements or {}),
            max_violations=max_violations,
            penalty_description=penalty_description,
        )
        session.add(reg)
        await session.commit()
        return reg.id


async def list_regulations(regulation_type: str | None = None, status: str = "active") -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Regulation).where(Regulation.status == status)
        if regulation_type:
            stmt = stmt.where(Regulation.regulation_type == regulation_type)
        result = await session.execute(stmt)
        return [
            {
                "id": r.id, "name": r.name, "description": r.description,
                "regulation_type": r.regulation_type, "authority_id": r.authority_id,
                "target_sector": r.target_sector,
                "requirements": json.loads(r.requirements) if r.requirements else {},
                "max_violations": r.max_violations,
                "penalty_description": r.penalty_description,
                "status": r.status,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in result.scalars().all()
        ]


async def create_conflict(plaintiff_id: str, plaintiff_type: str, defendant_id: str,
                          defendant_type: str, conflict_type: str,
                          description: str | None = None,
                          resolution_method: str = "arbitration") -> str:
    async with async_session_factory() as session:
        conflict = Conflict(
            plaintiff_id=plaintiff_id, plaintiff_type=plaintiff_type,
            defendant_id=defendant_id, defendant_type=defendant_type,
            conflict_type=conflict_type, description=description,
            resolution_method=resolution_method,
        )
        session.add(conflict)
        await session.commit()
        return conflict.id


async def get_conflict(conflict_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Conflict).where(Conflict.id == conflict_id))
        c = result.scalar_one_or_none()
        if not c:
            return None
        return _conflict_to_dict(c)


async def list_conflicts(status: str | None = None, party_id: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Conflict)
        conditions = []
        if status:
            conditions.append(Conflict.status == status)
        if party_id:
            from sqlalchemy import or_
            conditions.append(or_(Conflict.plaintiff_id == party_id, Conflict.defendant_id == party_id))
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.order_by(Conflict.created_at.desc())
        result = await session.execute(stmt)
        return [_conflict_to_dict(c) for c in result.scalars().all()]


async def update_conflict(conflict_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Conflict).where(Conflict.id == conflict_id))
        c = result.scalar_one_or_none()
        if c:
            for k, v in kwargs.items():
                if hasattr(c, k):
                    setattr(c, k, v)
            await session.commit()


async def create_vote(proposal_title: str, description: str | None, proposer_id: str,
                      proposal_type: str = "law", target_id: str | None = None,
                      options: list[str] | None = None, total_eligible: int = 0,
                      quorum_pct: float = 30.0, weight_factor: str = "equal") -> str:
    async with async_session_factory() as session:
        vote = Vote(
            proposal_title=proposal_title, description=description,
            proposer_id=proposer_id, proposal_type=proposal_type,
            target_id=target_id,
            options=json.dumps(options or ["yes", "no"]),
            total_eligible=total_eligible, quorum_pct=quorum_pct,
            weight_factor=weight_factor,
        )
        session.add(vote)
        await session.commit()
        return vote.id


async def get_vote(vote_id: str) -> dict | None:
    async with async_session_factory() as session:
        result = await session.execute(select(Vote).where(Vote.id == vote_id))
        v = result.scalar_one_or_none()
        if not v:
            return None
        return _vote_to_dict(v)


async def list_votes(status: str | None = None) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Vote)
        if status:
            stmt = stmt.where(Vote.status == status)
        stmt = stmt.order_by(Vote.created_at.desc())
        result = await session.execute(stmt)
        return [_vote_to_dict(v) for v in result.scalars().all()]


async def update_vote(vote_id: str, **kwargs) -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(Vote).where(Vote.id == vote_id))
        v = result.scalar_one_or_none()
        if v:
            for k, val in kwargs.items():
                if hasattr(v, k):
                    setattr(v, k, val)
            await session.commit()


async def record_governance(record_type: str, title: str, actor_id: str,
                            description: str | None = None, entity_id: str | None = None,
                            actor_type: str = "government",
                            related_ids: list[str] | None = None,
                            impact: dict | None = None) -> str:
    async with async_session_factory() as session:
        rec = GovernanceRecord(
            record_type=record_type, title=title, actor_id=actor_id,
            description=description, entity_id=entity_id,
            actor_type=actor_type,
            related_ids=json.dumps(related_ids or []),
            impact=json.dumps(impact or {}),
        )
        session.add(rec)
        await session.commit()
        return rec.id


async def get_governance_records(record_type: str | None = None, limit: int = 30) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(GovernanceRecord)
        if record_type:
            stmt = stmt.where(GovernanceRecord.record_type == record_type)
        stmt = stmt.order_by(GovernanceRecord.created_at.desc()).limit(limit)
        result = await session.execute(stmt)
        return [
            {
                "id": r.id, "record_type": r.record_type, "title": r.title,
                "description": r.description, "actor_id": r.actor_id,
                "actor_type": r.actor_type, "entity_id": r.entity_id,
                "related_ids": json.loads(r.related_ids) if r.related_ids else [],
                "impact": json.loads(r.impact) if r.impact else {},
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in result.scalars().all()
        ]


async def get_governance_stats() -> dict:
    async with async_session_factory() as session:
        entities = await session.execute(select(func.count(GovernanceEntity.id)))
        laws = await session.execute(select(func.count(Law.id)))
        policies = await session.execute(select(func.count(Policy.id)))
        taxes = await session.execute(select(func.count(Tax.id)))
        regulations = await session.execute(select(func.count(Regulation.id)))
        conflicts = await session.execute(select(func.count(Conflict.id)))
        votes = await session.execute(select(func.count(Vote.id)))
        total_tax_rev = await session.execute(select(func.sum(Tax.revenue_total)))
        return {
            "total_entities": entities.scalar() or 0,
            "total_laws": laws.scalar() or 0,
            "total_policies": policies.scalar() or 0,
            "total_taxes": taxes.scalar() or 0,
            "total_regulations": regulations.scalar() or 0,
            "total_conflicts": conflicts.scalar() or 0,
            "total_votes": votes.scalar() or 0,
            "total_tax_revenue": total_tax_rev.scalar() or 0.0,
        }


def _entity_to_dict(e: GovernanceEntity) -> dict:
    return {
        "id": e.id, "name": e.name, "entity_type": e.entity_type,
        "description": e.description, "authority_level": e.authority_level,
        "founder_id": e.founder_id,
        "member_ids": json.loads(e.member_ids) if e.member_ids else [],
        "policy_ids": json.loads(e.policy_ids) if e.policy_ids else [],
        "law_ids": json.loads(e.law_ids) if e.law_ids else [],
        "resources": json.loads(e.resources) if e.resources else {},
        "reputation": e.reputation, "status": e.status,
        "created_at": e.created_at.isoformat() if e.created_at else None,
    }


def _law_to_dict(l: Law) -> dict:
    return {
        "id": l.id, "name": l.name, "description": l.description,
        "creator_id": l.creator_id, "creator_type": l.creator_type,
        "scope": l.scope, "category": l.category, "severity": l.severity,
        "affected_entities": json.loads(l.affected_entities) if l.affected_entities else [],
        "penalty": json.loads(l.penalty) if l.penalty else {},
        "status": l.status,
        "created_at": l.created_at.isoformat() if l.created_at else None,
    }


def _policy_to_dict(p: Policy) -> dict:
    return {
        "id": p.id, "name": p.name, "description": p.description,
        "policy_type": p.policy_type, "creator_id": p.creator_id,
        "target": p.target, "rules": json.loads(p.rules) if p.rules else {},
        "expected_outcome": p.expected_outcome,
        "duration_days": p.duration_days, "priority": p.priority,
        "status": p.status, "compliance_rate": p.compliance_rate,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def _conflict_to_dict(c: Conflict) -> dict:
    return {
        "id": c.id, "plaintiff_id": c.plaintiff_id,
        "plaintiff_type": c.plaintiff_type,
        "defendant_id": c.defendant_id, "defendant_type": c.defendant_type,
        "conflict_type": c.conflict_type, "description": c.description,
        "evidence": json.loads(c.evidence) if c.evidence else [],
        "resolution_method": c.resolution_method,
        "resolution": c.resolution, "ruling": c.ruling,
        "penalty_amount": c.penalty_amount,
        "arbitrator_id": c.arbitrator_id, "status": c.status,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None,
    }


def _vote_to_dict(v: Vote) -> dict:
    return {
        "id": v.id, "proposal_title": v.proposal_title,
        "description": v.description, "proposer_id": v.proposer_id,
        "proposal_type": v.proposal_type, "target_id": v.target_id,
        "options": json.loads(v.options) if v.options else ["yes", "no"],
        "voters": json.loads(v.voters) if v.voters else {},
        "tally": json.loads(v.tally) if v.tally else {},
        "total_eligible": v.total_eligible, "quorum_pct": v.quorum_pct,
        "status": v.status, "result": v.result,
        "weight_factor": v.weight_factor,
        "created_at": v.created_at.isoformat() if v.created_at else None,
    }
