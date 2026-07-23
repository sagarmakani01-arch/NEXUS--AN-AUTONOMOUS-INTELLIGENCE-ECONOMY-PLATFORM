from sqlalchemy import select
from app.core.database import async_session_factory
from app.domain.models.identity import Identity
from app.domain.models.personality import Personality
from app.domain.models.goal import Goal
from app.domain.models.memory_entry import AgentMemory
from app.domain.models.relationship import Relationship
from app.domain.models.agent_skill_profile import AgentSkill
from app.domain.models.timeline_event import TimelineEvent
import uuid
import json
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _calc_strength(trust, respect, collabs, conflicts):
    raw = (trust + respect) / 2 + min(20, collabs * 3) - min(30, conflicts * 5)
    return max(0, min(100, raw))


# ── Save functions ──────────────────────────────────────────────────────────


async def save_identity(agent_id: str, data: dict):
    async with async_session_factory() as session:
        stmt = select(Identity).where(Identity.agent_id == agent_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row:
            for key, value in data.items():
                if hasattr(row, key):
                    setattr(row, key, value)
        else:
            row = Identity(id=str(uuid.uuid4()), agent_id=agent_id, **{
                k: v for k, v in data.items()
                if k in [c.key for c in Identity.__table__.columns]
            })
            session.add(row)

        await session.commit()


async def save_personality(agent_id: str, traits: dict):
    async with async_session_factory() as session:
        stmt = select(Personality).where(Personality.agent_id == agent_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row:
            row.traits = json.dumps(traits)
            for key, value in traits.items():
                if hasattr(row, key):
                    setattr(row, key, value)
            row.updated_at = datetime.now(timezone.utc)
        else:
            col_names = {c.key for c in Personality.__table__.columns}
            filtered = {k: v for k, v in traits.items() if k in col_names}
            row = Personality(
                id=str(uuid.uuid4()),
                agent_id=agent_id,
                traits=json.dumps(traits),
                **filtered,
            )
            session.add(row)

        await session.commit()


async def save_goal(agent_id: str, goal_data: dict):
    async with async_session_factory() as session:
        stmt = (
            select(Goal)
            .where(Goal.agent_id == agent_id, Goal.is_active == True)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row:
            for key, value in goal_data.items():
                if hasattr(row, key):
                    setattr(row, key, value)
            row.updated_at = datetime.now(timezone.utc)
        else:
            col_names = {c.key for c in Goal.__table__.columns}
            filtered = {k: v for k, v in goal_data.items() if k in col_names}
            row = Goal(
                id=str(uuid.uuid4()),
                agent_id=agent_id,
                is_active=True,
                **filtered,
            )
            session.add(row)

        await session.commit()


async def save_skills(agent_id: str, skills: list[dict]):
    async with async_session_factory() as session:
        stmt = select(AgentSkill).where(AgentSkill.agent_id == agent_id)
        result = await session.execute(stmt)
        existing = {s.skill_name: s for s in result.scalars().all()}

        seen = set()
        col_names = {c.key for c in AgentSkill.__table__.columns}

        for skill in skills:
            name = skill["skill_name"]
            seen.add(name)
            if name in existing:
                for key, value in skill.items():
                    if key in col_names and key != "id":
                        setattr(existing[name], key, value)
            else:
                filtered = {k: v for k, v in skill.items() if k in col_names}
                row = AgentSkill(
                    id=str(uuid.uuid4()),
                    agent_id=agent_id,
                    **filtered,
                )
                session.add(row)

        for name, row in existing.items():
            if name not in seen:
                await session.delete(row)

        await session.commit()


async def save_memory(
    agent_id: str,
    category: str,
    importance: str,
    title: str,
    description: str,
    related_agent_id: str | None = None,
) -> str:
    async with async_session_factory() as session:
        memory_id = str(uuid.uuid4())
        row = AgentMemory(
            id=memory_id,
            agent_id=agent_id,
            category=category,
            importance=importance,
            title=title,
            description=description,
            related_agent_id=related_agent_id,
        )
        session.add(row)
        await session.commit()
        return memory_id


async def save_timeline_event(
    agent_id: str,
    day: int,
    event_type: str,
    title: str,
    description: str,
):
    async with async_session_factory() as session:
        row = TimelineEvent(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            day=day,
            event_type=event_type,
            title=title,
            description=description,
        )
        session.add(row)
        await session.commit()


async def save_relationship(
    agent_a_id: str,
    agent_b_id: str,
    trust: float,
    respect: float,
    strength: float,
):
    async with async_session_factory() as session:
        pair = tuple(sorted([agent_a_id, agent_b_id]))
        stmt = select(Relationship).where(
            Relationship.agent_a_id == pair[0],
            Relationship.agent_b_id == pair[1],
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row:
            row.trust = trust
            row.respect = respect
            row.strength = strength
            row.last_interaction = datetime.now(timezone.utc)
        else:
            row = Relationship(
                id=str(uuid.uuid4()),
                agent_a_id=pair[0],
                agent_b_id=pair[1],
                trust=trust,
                respect=respect,
                strength=strength,
                collaboration_count=0,
                conflict_count=0,
            )
            session.add(row)

        await session.commit()


async def update_relationship_on_interaction(
    agent_a_id: str, agent_b_id: str, interaction_type: str
):
    async with async_session_factory() as session:
        pair = tuple(sorted([agent_a_id, agent_b_id]))
        stmt = select(Relationship).where(
            Relationship.agent_a_id == pair[0],
            Relationship.agent_b_id == pair[1],
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row is None:
            row = Relationship(
                id=str(uuid.uuid4()),
                agent_a_id=pair[0],
                agent_b_id=pair[1],
                trust=50.0,
                respect=50.0,
                strength=50.0,
                collaboration_count=0,
                conflict_count=0,
            )
            session.add(row)

        if interaction_type == "collaboration":
            row.collaboration_count = (row.collaboration_count or 0) + 1
            row.trust = min(100, (row.trust or 50) + 2)
            row.respect = min(100, (row.respect or 50) + 1)
        elif interaction_type == "conflict":
            row.conflict_count = (row.conflict_count or 0) + 1
            row.trust = max(0, (row.trust or 50) - 5)
            row.respect = max(0, (row.respect or 50) - 3)

        row.strength = _calc_strength(
            row.trust or 50, row.respect or 50,
            row.collaboration_count or 0, row.conflict_count or 0
        )
        row.last_interaction = datetime.now(timezone.utc)

        await session.commit()


# ── Load functions ──────────────────────────────────────────────────────────


async def load_all_identities() -> dict[str, dict]:
    async with async_session_factory() as session:
        stmt = select(Identity)
        result = await session.execute(stmt)
        rows = result.scalars().all()

        return {
            row.agent_id: {
                col.key: getattr(row, col.key)
                for col in Identity.__table__.columns
            }
            for row in rows
        }


async def load_personality(agent_id: str) -> dict:
    async with async_session_factory() as session:
        stmt = select(Personality).where(Personality.agent_id == agent_id)
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row is None:
            return {}
        if row.traits:
            parsed = json.loads(row.traits) if isinstance(row.traits, str) else row.traits
            return parsed
        return {
            col.key: getattr(row, col.key)
            for col in Personality.__table__.columns
            if col.key not in ("id", "agent_id", "created_at", "updated_at", "traits")
        }


async def load_goal(agent_id: str) -> dict:
    async with async_session_factory() as session:
        stmt = (
            select(Goal)
            .where(Goal.agent_id == agent_id, Goal.is_active == True)
            .order_by(Goal.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.scalar_one_or_none()

        if row is None:
            return {}
        return {
            "title": row.title,
            "category": row.category,
            "progress": row.progress,
            "target": row.target,
        }


async def load_skills(agent_id: str) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(AgentSkill).where(AgentSkill.agent_id == agent_id)
        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [
            {
                "skill_name": row.skill_name,
                "level": row.level,
                "experience": row.experience,
                "max_experience": row.max_experience,
                "learning_progress": row.learning_progress,
                "certified": row.certified,
            }
            for row in rows
        ]


async def load_memories(agent_id: str, limit: int = 50) -> list[dict]:
    async with async_session_factory() as session:
        stmt = (
            select(AgentMemory)
            .where(AgentMemory.agent_id == agent_id)
            .order_by(AgentMemory.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [
            {
                "id": row.id,
                "agent_id": row.agent_id,
                "category": row.category,
                "title": row.title,
                "description": row.description,
                "importance": row.importance,
                "related_agent_id": row.related_agent_id,
                "created_at": str(row.created_at) if row.created_at else "",
            }
            for row in rows
        ]


async def load_timeline(agent_id: str) -> list[dict]:
    async with async_session_factory() as session:
        stmt = (
            select(TimelineEvent)
            .where(TimelineEvent.agent_id == agent_id)
            .order_by(TimelineEvent.day.desc())
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()

        return [
            {
                "id": row.id,
                "agent_id": row.agent_id,
                "day": row.day,
                "event_type": row.event_type,
                "title": row.title,
                "description": row.description,
                "created_at": str(row.created_at) if row.created_at else "",
            }
            for row in rows
        ]


async def load_relationships(agent_id: str) -> list[dict]:
    async with async_session_factory() as session:
        stmt = select(Relationship).where(
            (Relationship.agent_a_id == agent_id) | (Relationship.agent_b_id == agent_id)
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()

        relationships = []
        for row in rows:
            other = row.agent_b_id if row.agent_a_id == agent_id else row.agent_a_id
            relationships.append({
                "other_agent_id": other,
                "trust": row.trust,
                "respect": row.respect,
                "strength": row.strength,
                "collaboration_count": row.collaboration_count,
                "conflict_count": row.conflict_count,
            })

        return relationships
