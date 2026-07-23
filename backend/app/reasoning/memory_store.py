from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, desc

from app.core.database import async_session_factory
from app.domain.models.decision import Decision

logger = logging.getLogger("nexus.reasoning.memory_store")


class DecisionMemoryStore:
    async def store(self, decision_data: dict) -> str:
        decision_id = str(uuid.uuid4())
        try:
            async with async_session_factory() as session:
                row = Decision(
                    id=decision_id,
                    agent_id=decision_data["agent_id"],
                    trigger_type=decision_data.get("trigger_type", ""),
                    trigger_id=decision_data.get("trigger_id"),
                    decision=decision_data.get("decision", ""),
                    reasoning_summary=decision_data.get("reasoning_summary", ""),
                    confidence=decision_data.get("confidence", 0.5),
                    expected_outcome=decision_data.get("expected_outcome", ""),
                    risk_level=decision_data.get("risk_level", "medium"),
                    estimated_cost=decision_data.get("estimated_cost", 0),
                    estimated_reward=decision_data.get("estimated_reward", 0),
                    next_goal=decision_data.get("next_goal", ""),
                    alternative_options=json.dumps(decision_data.get("alternative_options", [])),
                    context_snapshot=json.dumps(decision_data.get("context_snapshot", {})),
                    provider_used=decision_data.get("provider_used", "deterministic"),
                    reasoning_duration_ms=decision_data.get("reasoning_duration_ms", 0),
                    status=decision_data.get("status", "pending"),
                )
                session.add(row)
                await session.commit()
                return decision_id
        except Exception as exc:
            logger.error("store_decision_error: %s", exc)
            return decision_id

    async def get(self, decision_id: str) -> dict | None:
        async with async_session_factory() as session:
            stmt = select(Decision).where(Decision.id == decision_id)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            if not row:
                return None
            return self._row_to_dict(row)

    async def get_agent_decisions(
        self, agent_id: str, limit: int = 50, offset: int = 0
    ) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(Decision)
                .where(Decision.agent_id == agent_id)
                .order_by(desc(Decision.created_at))
                .limit(limit)
                .offset(offset)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._row_to_dict(r) for r in rows]

    async def get_by_trigger_type(
        self, agent_id: str, trigger_type: str, limit: int = 20
    ) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(Decision)
                .where(Decision.agent_id == agent_id, Decision.trigger_type == trigger_type)
                .order_by(desc(Decision.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._row_to_dict(r) for r in rows]

    async def get_recent(self, agent_id: str, hours: int = 24, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(Decision)
                .where(Decision.agent_id == agent_id)
                .order_by(desc(Decision.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._row_to_dict(r) for r in rows]

    async def get_successful(self, agent_id: str, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(Decision)
                .where(Decision.agent_id == agent_id, Decision.status == "completed")
                .order_by(desc(Decision.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._row_to_dict(r) for r in rows]

    async def get_failed(self, agent_id: str, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(Decision)
                .where(Decision.agent_id == agent_id, Decision.status == "failed")
                .order_by(desc(Decision.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [self._row_to_dict(r) for r in rows]

    async def update_status(self, decision_id: str, status: str) -> None:
        try:
            async with async_session_factory() as session:
                stmt = select(Decision).where(Decision.id == decision_id)
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row:
                    row.status = status
                    await session.commit()
        except Exception as exc:
            logger.error("update_decision_status_error: %s", exc)

    async def search(self, agent_id: str, query: str, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(Decision)
                .where(Decision.agent_id == agent_id)
                .order_by(desc(Decision.created_at))
                .limit(200)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()

            query_lower = query.lower()
            matched = []
            for row in rows:
                searchable = " ".join([
                    row.decision or "",
                    row.reasoning_summary or "",
                    row.trigger_type or "",
                    row.expected_outcome or "",
                ]).lower()
                if query_lower in searchable:
                    matched.append(self._row_to_dict(row))
                if len(matched) >= limit:
                    break
            return matched

    def _row_to_dict(self, row: Decision) -> dict:
        alt_opts = row.alternative_options
        if isinstance(alt_opts, str):
            try:
                alt_opts = json.loads(alt_opts)
            except (json.JSONDecodeError, TypeError):
                alt_opts = []

        ctx = row.context_snapshot
        if isinstance(ctx, str):
            try:
                ctx = json.loads(ctx)
            except (json.JSONDecodeError, TypeError):
                ctx = {}

        return {
            "id": row.id,
            "agent_id": row.agent_id,
            "trigger_type": row.trigger_type,
            "trigger_id": row.trigger_id,
            "decision": row.decision,
            "reasoning_summary": row.reasoning_summary,
            "confidence": row.confidence,
            "expected_outcome": row.expected_outcome,
            "risk_level": row.risk_level,
            "estimated_cost": row.estimated_cost,
            "estimated_reward": row.estimated_reward,
            "next_goal": row.next_goal,
            "alternative_options": alt_opts,
            "context_snapshot": ctx,
            "provider_used": row.provider_used,
            "reasoning_duration_ms": row.reasoning_duration_ms,
            "status": row.status,
            "created_at": str(row.created_at) if row.created_at else "",
        }
