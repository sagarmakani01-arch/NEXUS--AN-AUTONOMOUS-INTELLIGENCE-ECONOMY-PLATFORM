from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.database import async_session_factory
from app.domain.models.reflection import Reflection
from app.domain.models.decision import Decision

logger = logging.getLogger("nexus.reasoning.reflection")


class ReflectionEngine:
    async def reflect(
        self,
        agent_id: str,
        decision_id: str,
        plan_id: str | None,
        expected_outcome: str,
        actual_outcome: str,
        success: bool,
        cost_actual: float = 0,
        reward_actual: float = 0,
    ) -> dict:
        lessons = self._extract_lessons(expected_outcome, actual_outcome, success)
        failure_cause = None if success else self._identify_failure_cause(expected_outcome, actual_outcome)
        experience_gain = self._calc_experience_gain(success, cost_actual, reward_actual)
        success_rate = 1.0 if success else 0.0

        reflection_id = str(uuid.uuid4())
        reflection = {
            "id": reflection_id,
            "agent_id": agent_id,
            "decision_id": decision_id,
            "plan_id": plan_id,
            "expected_outcome": expected_outcome,
            "actual_outcome": actual_outcome,
            "lessons_learned": lessons,
            "success_rate": success_rate,
            "failure_cause": failure_cause,
            "experience_gain": experience_gain,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        await self._store_reflection(reflection)
        await self._update_decision_outcome(decision_id, actual_outcome, success)

        return reflection

    async def get_reflections(self, agent_id: str, limit: int = 20) -> list[dict]:
        async with async_session_factory() as session:
            stmt = (
                select(Reflection)
                .where(Reflection.agent_id == agent_id)
                .order_by(Reflection.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            rows = result.scalars().all()

            return [
                {
                    "id": row.id,
                    "agent_id": row.agent_id,
                    "decision_id": row.decision_id,
                    "plan_id": row.plan_id,
                    "expected_outcome": row.expected_outcome,
                    "actual_outcome": row.actual_outcome,
                    "lessons_learned": json.loads(row.lessons_learned) if isinstance(row.lessons_learned, str) else (row.lessons_learned or []),
                    "success_rate": row.success_rate,
                    "failure_cause": row.failure_cause,
                    "experience_gain": row.experience_gain,
                    "created_at": str(row.created_at) if row.created_at else "",
                }
                for row in rows
            ]

    async def get_success_rate(self, agent_id: str) -> float:
        async with async_session_factory() as session:
            stmt = select(Reflection).where(Reflection.agent_id == agent_id)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            if not rows:
                return 0.5
            total = len(rows)
            successes = sum(1 for r in rows if r.success_rate >= 0.5)
            return round(successes / total, 3)

    async def get_lessons_summary(self, agent_id: str) -> list[str]:
        reflections = await self.get_reflections(agent_id, limit=50)
        all_lessons = []
        for r in reflections:
            lessons = r.get("lessons_learned", [])
            if isinstance(lessons, str):
                try:
                    lessons = json.loads(lessons)
                except (json.JSONDecodeError, TypeError):
                    lessons = [lessons]
            all_lessons.extend(lessons)
        seen = set()
        unique = []
        for lesson in all_lessons:
            if lesson not in seen:
                seen.add(lesson)
                unique.append(lesson)
        return unique[:20]

    def _extract_lessons(self, expected: str, actual: str, success: bool) -> list[str]:
        lessons = []
        if success:
            lessons.append("Decision led to successful outcome")
            if expected and actual:
                if expected.lower() in actual.lower():
                    lessons.append("Outcome matched expectations well")
                else:
                    lessons.append("Outcome differed from expectations but was still positive")
        else:
            lessons.append("Decision did not achieve desired outcome")
            if expected and actual:
                lessons.append(f"Expected: {expected[:80]}")
                lessons.append(f"Actual: {actual[:80]}")
        return lessons

    def _identify_failure_cause(self, expected: str, actual: str) -> str:
        if not actual:
            return "No outcome recorded"
        if "energy" in actual.lower():
            return "Insufficient energy to complete task"
        if "budget" in actual.lower() or "cost" in actual.lower():
            return "Budget constraints prevented completion"
        if "time" in actual.lower():
            return "Time constraints prevented completion"
        if "rejected" in actual.lower() or "denied" in actual.lower():
            return "Decision was rejected by the system"
        return "Outcome did not match expectations"

    def _calc_experience_gain(self, success: bool, cost: float, reward: float) -> float:
        base = 10.0 if success else 3.0
        reward_bonus = min(5.0, reward / 10.0)
        cost_penalty = min(3.0, cost / 20.0)
        return round(base + reward_bonus - cost_penalty, 2)

    async def _store_reflection(self, reflection: dict) -> None:
        try:
            async with async_session_factory() as session:
                row = Reflection(
                    id=reflection["id"],
                    agent_id=reflection["agent_id"],
                    decision_id=reflection.get("decision_id"),
                    plan_id=reflection.get("plan_id"),
                    expected_outcome=reflection.get("expected_outcome"),
                    actual_outcome=reflection.get("actual_outcome"),
                    lessons_learned=json.dumps(reflection.get("lessons_learned", [])),
                    success_rate=reflection.get("success_rate", 0),
                    failure_cause=reflection.get("failure_cause"),
                    experience_gain=reflection.get("experience_gain", 0),
                )
                session.add(row)
                await session.commit()
        except Exception as exc:
            logger.error("store_reflection_error: %s", exc)

    async def _update_decision_outcome(self, decision_id: str, outcome: str, success: bool) -> None:
        try:
            async with async_session_factory() as session:
                stmt = select(Decision).where(Decision.id == decision_id)
                result = await session.execute(stmt)
                row = result.scalar_one_or_none()
                if row:
                    row.expected_outcome = outcome
                    row.status = "completed" if success else "failed"
                    await session.commit()
        except Exception as exc:
            logger.error("update_decision_outcome_error: %s", exc)
