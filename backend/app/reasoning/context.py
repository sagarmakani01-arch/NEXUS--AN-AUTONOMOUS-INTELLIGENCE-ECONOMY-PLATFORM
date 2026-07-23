from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from app.reasoning.triggers import DecisionTrigger

if TYPE_CHECKING:
    from app.reasoning.memory import MemoryRetriever
    from app.simulation.engine import SimulationEngine

logger = logging.getLogger("nexus.reasoning.context")

CONTEXT_PRIORITY_ORDER = [
    "identity",
    "current_goal",
    "personality",
    "current_situation",
    "memories",
    "relationships",
    "history",
    "wallet",
    "skills",
    "nearby_events",
    "recent_decisions",
    "current_plan",
    "simulation_time",
]


class ContextFilter:
    def estimate_tokens(self, context: dict) -> int:
        raw = json.dumps(context, default=str)
        return max(1, len(raw) // 4)

    def filter_by_relevance(self, context: dict, max_tokens: int = 4000) -> dict:
        current_tokens = self.estimate_tokens(context)
        if current_tokens <= max_tokens:
            return context

        filtered: dict = {}
        for section in CONTEXT_PRIORITY_ORDER:
            if section not in context:
                continue
            filtered[section] = context[section]
            if self.estimate_tokens(filtered) >= max_tokens:
                break

        if self.estimate_tokens(filtered) > max_tokens:
            filtered = self._truncate_section(filtered, max_tokens)

        return filtered

    def _truncate_section(self, context: dict, max_tokens: int) -> dict:
        result = {}
        token_budget = max_tokens
        for section, value in context.items():
            section_tokens = self.estimate_tokens({section: value})
            if section_tokens <= token_budget:
                result[section] = value
                token_budget -= section_tokens
            else:
                if isinstance(value, list) and len(value) > 0:
                    result[section] = value[: max(1, len(value) // 2)]
                    token_budget -= self.estimate_tokens({section: result[section]})
                elif isinstance(value, str) and len(value) > 200:
                    truncated = value[:200] + "..."
                    result[section] = truncated
                    token_budget -= self.estimate_tokens({section: truncated})
                if token_budget <= 0:
                    break
        return result


class ContextBuilder:
    def __init__(self, engine: SimulationEngine, memory_retriever: MemoryRetriever) -> None:
        self._engine = engine
        self._memory_retriever = memory_retriever
        self._filter = ContextFilter()

    async def build_context(self, agent_id: str, trigger: DecisionTrigger) -> dict:
        profile = self._engine.profiles.get(agent_id)
        if not profile:
            logger.warning("no_profile_found agent=%s", agent_id)
            return {"agent_id": agent_id, "error": "profile_not_found"}

        recent_decisions = await self._memory_retriever.get_short_term(agent_id, limit=5)
        trigger_memories = await self._memory_retriever.get_semantic(
            agent_id, trigger.trigger_type.value, limit=5
        )
        reflections = await self._memory_retriever.get_reflections(agent_id, limit=3)

        agent_obj = profile.agent

        context: dict = {
            "agent_id": agent_id,
            "identity": {
                "display_name": profile.identity.get("display_name", agent_obj.name),
                "first_name": profile.identity.get("first_name", ""),
                "last_name": profile.identity.get("last_name", ""),
                "generation": profile.identity.get("generation", 1),
                "profession": profile.identity.get("profession", ""),
                "profession_category": profile.identity.get("profession_category", ""),
                "status": profile.identity.get("status", "active"),
            },
            "personality": profile.personality,
            "skills": profile.skills,
            "wallet": {
                "balance": agent_obj.wallet_balance,
                "reputation": agent_obj.reputation,
                "trust_score": profile.trust_score,
            },
            "current_goal": profile.goal,
            "memories": trigger_memories,
            "recent_decisions": recent_decisions,
            "reflections": reflections,
            "current_situation": {
                "energy": agent_obj.energy,
                "status": agent_obj.current_status,
                "current_task": agent_obj.current_goal,
            },
            "relationships": await self._load_relationships(agent_id),
            "simulation_time": trigger.context.get("simulation_time", ""),
            "nearby_events": trigger.context.get("nearby_events", []),
            "current_plan": trigger.context.get("current_plan"),
            "trigger": trigger.to_dict(),
        }

        return self._filter.filter_by_relevance(context, max_tokens=4000)

    async def _load_relationships(self, agent_id: str) -> list[dict]:
        try:
            from app.simulation.persistence import load_relationships

            relationships = await load_relationships(agent_id)
            enriched = []
            for rel in relationships:
                other_id = rel.get("other_agent_id", "")
                other_profile = self._engine.profiles.get(other_id)
                if other_profile:
                    rel["other_name"] = other_profile.identity.get("display_name", other_id)
                    rel["other_profession"] = other_profile.identity.get("profession", "")
                enriched.append(rel)
            return enriched
        except Exception as exc:
            logger.error("load_relationships_error agent=%s err=%s", agent_id, exc)
            return []
