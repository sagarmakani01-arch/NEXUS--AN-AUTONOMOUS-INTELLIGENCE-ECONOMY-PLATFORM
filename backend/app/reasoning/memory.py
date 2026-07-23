from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.domain.models.decision import Decision
from app.domain.models.reflection import Reflection
from app.reasoning.triggers import (
    DecisionTrigger,
    RELATED_TRIGGERS,
    TriggerType,
)

logger = logging.getLogger("nexus.reasoning.memory")


class MemoryRetriever:
    def __init__(self, async_session_factory: async_sessionmaker) -> None:
        self._session_factory = async_session_factory

    async def get_short_term(self, agent_id: str, limit: int = 10) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        async with self._session_factory() as session:
            result = await session.execute(
                select(Decision)
                .where(Decision.agent_id == agent_id)
                .where(Decision.created_at >= cutoff)
                .order_by(desc(Decision.created_at))
                .limit(limit)
            )
            return [self._decision_to_dict(r) for r in result.scalars().all()]

    async def get_long_term(self, agent_id: str, limit: int = 10) -> list[dict]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Decision)
                .where(Decision.agent_id == agent_id)
                .where(Decision.status == "completed")
                .order_by(desc(Decision.confidence))
                .limit(limit)
            )
            return [self._decision_to_dict(r) for r in result.scalars().all()]

    async def get_semantic(self, agent_id: str, query: str, limit: int = 5) -> list[dict]:
        query_lower = query.lower()
        keywords = set(query_lower.split())

        async with self._session_factory() as session:
            result = await session.execute(
                select(Decision)
                .where(Decision.agent_id == agent_id)
                .order_by(desc(Decision.created_at))
                .limit(100)
            )
            decisions = result.scalars().all()

        scored: list[tuple[float, dict]] = []
        for d in decisions:
            d_dict = self._decision_to_dict(d)
            score = self._keyword_score(d_dict, keywords, query_lower)
            if score > 0:
                scored.append((score, d_dict))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:limit]]

    async def get_procedural(self, agent_id: str, skill: str = "", limit: int = 5) -> list[dict]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Decision)
                .where(Decision.agent_id == agent_id)
                .where(Decision.trigger_type.in_(["skill_selection", "task_acceptance", "contract_offer"]))
                .order_by(desc(Decision.created_at))
                .limit(50)
            )
            decisions = result.scalars().all()

        if not skill:
            return [self._decision_to_dict(d) for d in decisions[:limit]]

        skill_lower = skill.lower()
        filtered = [
            d for d in decisions
            if skill_lower in (d.decision or "").lower()
            or skill_lower in (d.reasoning_summary or "").lower()
            or skill_lower in json.dumps(d.context_snapshot or "{}").lower()
        ]
        return [self._decision_to_dict(d) for d in filtered[:limit]]

    async def get_reflections(self, agent_id: str, limit: int = 5) -> list[dict]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(Reflection)
                .where(Reflection.agent_id == agent_id)
                .order_by(desc(Reflection.created_at))
                .limit(limit)
            )
            return [self._reflection_to_dict(r) for r in result.scalars().all()]

    async def retrieve_all(
        self, agent_id: str, trigger_type: str = "", limit: int = 20
    ) -> list[dict]:
        seen_ids: set[str] = set()
        combined: list[dict] = []

        short_term = await self.get_short_term(agent_id, limit=limit)
        for m in short_term:
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                combined.append(m)

        long_term = await self.get_long_term(agent_id, limit=limit)
        for m in long_term:
            if m["id"] not in seen_ids:
                seen_ids.add(m["id"])
                combined.append(m)

        reflections = await self.get_reflections(agent_id, limit=limit)
        for r in reflections:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                combined.append(r)

        if trigger_type:
            semantic = await self.get_semantic(agent_id, trigger_type, limit=limit)
            for m in semantic:
                if m["id"] not in seen_ids:
                    seen_ids.add(m["id"])
                    combined.append(m)

        return combined[:limit]

    async def rank_by_relevance(
        self, memories: list[dict], trigger: DecisionTrigger
    ) -> list[dict]:
        scored: list[tuple[float, dict]] = []
        now = datetime.now(timezone.utc)

        for mem in memories:
            score = 0.0
            mem_trigger = mem.get("trigger_type", "")

            if mem_trigger == trigger.trigger_type.value:
                score += 3.0
            elif mem_trigger in [t.value for t in RELATED_TRIGGERS.get(trigger.trigger_type, [])]:
                score += 1.0

            created = mem.get("created_at", "")
            if created:
                try:
                    mem_time = datetime.fromisoformat(created)
                    if mem_time.tzinfo is None:
                        mem_time = mem_time.replace(tzinfo=timezone.utc)
                    hours_ago = (now - mem_time).total_seconds() / 3600
                    if hours_ago < 1:
                        score += 2.0
                    elif hours_ago < 24:
                        score += 1.5
                    elif hours_ago < 168:
                        score += 0.5
                except (ValueError, TypeError):
                    pass

            importance = mem.get("importance", "medium")
            if importance == "high":
                score += 2.0
            elif importance == "medium":
                score += 1.0

            expected = mem.get("expected_outcome", "")
            actual = mem.get("actual_outcome", "")
            if expected and actual:
                score += 1.0

            scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored]

    def _decision_to_dict(self, decision: Decision) -> dict:
        return {
            "id": decision.id,
            "agent_id": decision.agent_id,
            "trigger_type": decision.trigger_type,
            "trigger_id": decision.trigger_id,
            "decision": decision.decision,
            "reasoning_summary": decision.reasoning_summary,
            "confidence": decision.confidence,
            "expected_outcome": decision.expected_outcome,
            "risk_level": decision.risk_level,
            "estimated_cost": decision.estimated_cost,
            "estimated_reward": decision.estimated_reward,
            "next_goal": decision.next_goal,
            "alternative_options": decision.alternative_options,
            "context_snapshot": decision.context_snapshot,
            "provider_used": decision.provider_used,
            "reasoning_duration_ms": decision.reasoning_duration_ms,
            "status": decision.status,
            "created_at": decision.created_at.isoformat() if decision.created_at else "",
        }

    def _reflection_to_dict(self, reflection: Reflection) -> dict:
        return {
            "id": reflection.id,
            "agent_id": reflection.agent_id,
            "decision_id": reflection.decision_id,
            "plan_id": reflection.plan_id,
            "expected_outcome": reflection.expected_outcome,
            "actual_outcome": reflection.actual_outcome,
            "lessons_learned": reflection.lessons_learned,
            "success_rate": reflection.success_rate,
            "failure_cause": reflection.failure_cause,
            "experience_gain": reflection.experience_gain,
            "created_at": reflection.created_at.isoformat() if reflection.created_at else "",
        }

    def _keyword_score(self, record: dict, keywords: set[str], full_query: str) -> float:
        score = 0.0
        searchable = " ".join(
            str(record.get(field, "") or "")
            for field in ["trigger_type", "decision", "reasoning_summary", "expected_outcome", "next_goal"]
        ).lower()

        for kw in keywords:
            if kw in searchable:
                score += 1.0

        if full_query in searchable:
            score += 2.0

        return score
