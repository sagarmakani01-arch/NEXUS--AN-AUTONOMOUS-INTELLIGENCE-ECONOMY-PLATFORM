from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field

from app.reasoning.context import ContextBuilder, ContextFilter
from app.reasoning.memory import MemoryRetriever
from app.reasoning.memory_store import DecisionMemoryStore
from app.reasoning.planning import PlanningEngine
from app.reasoning.prompts import PromptBuilder
from app.reasoning.providers.factory import get_provider
from app.reasoning.queue import ReasoningQueue, ReasoningTask
from app.reasoning.reflection import ReflectionEngine
from app.reasoning.triggers import DecisionTrigger, TriggerType, create_trigger
from app.reasoning.validator import DecisionValidator
from app.simulation.events import EventQueue, EventType, SimEvent

logger = logging.getLogger("nexus.reasoning")


@dataclass
class AgentReasoningState:
    agent_id: str
    current_decision: dict | None = None
    current_plan: dict | None = None
    last_reasoning_at: float = 0
    total_decisions: int = 0
    total_reflections: int = 0
    reasoning_status: str = "idle"
    provider_used: str = "deterministic"
    last_reasoning_duration_ms: float = 0


class ReasoningEngine:
    def __init__(self, sim_engine=None) -> None:
        self._sim_engine = sim_engine
        self._provider_name = "deterministic"
        self._provider = get_provider(self._provider_name)
        self._prompt_builder = PromptBuilder()
        self._context_builder: ContextBuilder | None = None
        self._memory_retriever: MemoryRetriever | None = None
        self._decision_store = DecisionMemoryStore()
        self._validator = DecisionValidator()
        self._planning_engine = PlanningEngine()
        self._reflection_engine = ReflectionEngine()
        self._queue = ReasoningQueue(max_size=500, max_concurrent=10, timeout_seconds=30.0)
        self._context_filter = ContextFilter()
        self._agent_states: dict[str, AgentReasoningState] = {}
        self._trigger_handlers: dict[str, callable] = {}
        self._running = False
        self._task: asyncio.Task | None = None
        self._sse_subscribers: list[asyncio.Queue] = []
        self._lock = asyncio.Lock()
        self._event_count = 0
        self._decision_count = 0
        self._reflection_count = 0

    def init(self) -> None:
        if self._sim_engine:
            self._context_builder = ContextBuilder(
                engine=self._sim_engine,
                memory_retriever=self._get_memory_retriever(),
            )

    def _get_memory_retriever(self) -> MemoryRetriever:
        if not self._memory_retriever:
            from app.core.database import async_session_factory
            self._memory_retriever = MemoryRetriever(async_session_factory)
        return self._memory_retriever

    async def start(self) -> None:
        if self._running:
            return
        async with self._lock:
            self._running = True
            self._task = asyncio.create_task(self._processing_loop())
            logger.info("reasoning_engine_started provider=%s", self._provider_name)

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("reasoning_engine_stopped")

    def set_provider(self, name: str) -> None:
        self._provider_name = name
        self._provider = get_provider(name)
        logger.info("reasoning_provider_changed provider=%s", name)

    def get_provider_info(self) -> dict:
        return {
            "name": self._provider_name,
            "available": self._provider.is_available,
        }

    async def trigger_decision(
        self,
        agent_id: str,
        trigger_type: str,
        context_data: dict | None = None,
        priority: int = 5,
    ) -> str:
        trigger = create_trigger(
            trigger_type=TriggerType(trigger_type),
            agent_id=agent_id,
            priority=priority,
            context=context_data or {},
        )

        task = ReasoningTask(
            task_id=trigger.trigger_id,
            agent_id=agent_id,
            trigger_type=trigger_type,
            trigger_id=trigger.trigger_id,
            priority=priority,
            context=context_data or {},
        )

        enqueued = await self._queue.enqueue(task)
        if not enqueued:
            logger.warning("trigger_rejected queue_full agent=%s", agent_id)
            return ""

        self._event_count += 1
        state = self._get_agent_state(agent_id)
        state.reasoning_status = "queued"

        await self._broadcast_sse({
            "type": "decision_triggered",
            "data": {
                "agent_id": agent_id,
                "trigger_type": trigger_type,
                "task_id": task.task_id,
                "priority": priority,
            },
        })

        return trigger.trigger_id

    async def reason(self, agent_id: str, trigger_type: str, context_data: dict | None = None) -> dict:
        state = self._get_agent_state(agent_id)
        state.reasoning_status = "reasoning"
        start_time = time.time()

        try:
            from app.resources.compute_manager import ComputeManager
            cm = ComputeManager()
            compute_result = await cm.consume(agent_id, trigger_type)
            if not compute_result.get("success"):
                state.reasoning_status = "idle"
                logger.info("insufficient_compute agent=%s trigger=%s", agent_id, trigger_type)
                return {
                    "decision": "continue",
                    "reasoning_summary": "Insufficient compute credits, using deterministic fallback",
                    "confidence": 0.3,
                    "expected_outcome": "Default behavior",
                    "risk_level": "low",
                    "estimated_cost": 0,
                    "estimated_reward": 0,
                    "next_goal": "",
                    "alternative_options": [],
                    "provider_used": "deterministic_fallback",
                    "status": "compute_limited",
                }

            context = await self._build_context(agent_id, trigger_type, context_data or {})

            memories = await self._get_memory_retriever().retrieve_all(
                agent_id, trigger_type=trigger_type, limit=10
            )
            ranked = await self._get_memory_retriever().rank_by_relevance(
                memories, create_trigger(
                    trigger_type=TriggerType(trigger_type),
                    agent_id=agent_id,
                )
            )
            context["memories"] = ranked[:8]

            prompt = self._prompt_builder.build(context, trigger_type)
            prompt_stats = self._prompt_builder.get_prompt_stats(prompt)
            logger.debug("prompt_stats agent=%s tokens=%d", agent_id, prompt_stats["estimated_tokens"])

            provider_result = await self._provider.generate(prompt)
            raw_decision = self._provider.parse_json_response(provider_result["text"])

            is_valid, errors, corrected = self._validator.validate(raw_decision, context, trigger_type)

            duration_ms = (time.time() - start_time) * 1000

            decision_data = {
                "agent_id": agent_id,
                "trigger_type": trigger_type,
                "trigger_id": context_data.get("trigger_id", ""),
                "decision": corrected.get("decision", "continue"),
                "reasoning_summary": corrected.get("reasoning_summary", ""),
                "confidence": corrected.get("confidence", 0.5),
                "expected_outcome": corrected.get("expected_outcome", ""),
                "risk_level": corrected.get("risk_level", "medium"),
                "estimated_cost": corrected.get("estimated_cost", 0),
                "estimated_reward": corrected.get("estimated_reward", 0),
                "next_goal": corrected.get("next_goal", ""),
                "alternative_options": corrected.get("alternative_options", []),
                "context_snapshot": {
                    "trigger_type": trigger_type,
                    "wallet_balance": context.get("agent", {}).get("wallet_balance", 0),
                    "energy": context.get("agent", {}).get("energy", 50),
                },
                "provider_used": self._provider_name,
                "reasoning_duration_ms": duration_ms,
                "status": "completed",
            }

            decision_id = await self._decision_store.store(decision_data)
            decision_data["id"] = decision_id

            state.current_decision = decision_data
            state.total_decisions += 1
            state.last_reasoning_at = time.time()
            state.reasoning_status = "idle"
            state.provider_used = self._provider_name
            state.last_reasoning_duration_ms = duration_ms
            self._decision_count += 1

            await self._broadcast_sse({
                "type": "decision_made",
                "data": decision_data,
            })

            return decision_data

        except Exception as exc:
            state.reasoning_status = "error"
            logger.error("reasoning_error agent=%s err=%s", agent_id, exc)
            return {
                "error": str(exc),
                "decision": "continue",
                "confidence": 0.3,
                "reasoning_summary": "Error occurred, falling back to default behavior",
            }

    async def create_plan(self, agent_id: str, goal: str, decision_id: str) -> dict:
        context = {}
        if self._sim_engine and agent_id in self._sim_engine.profiles:
            profile = self._sim_engine.profiles[agent_id]
            context = {
                "agent": profile.agent.to_dict(),
                "personality": profile.personality,
                "skills": profile.skills,
            }

        plan = self._planning_engine.create_plan(agent_id, goal, decision_id, context)
        state = self._get_agent_state(agent_id)
        state.current_plan = plan
        return plan

    async def advance_plan(self, agent_id: str) -> dict | None:
        state = self._get_agent_state(agent_id)
        if not state.current_plan:
            return None
        state.current_plan = self._planning_engine.advance_plan(state.current_plan)
        return state.current_plan

    async def reflect(
        self,
        agent_id: str,
        decision_id: str,
        expected_outcome: str,
        actual_outcome: str,
        success: bool,
        cost: float = 0,
        reward: float = 0,
    ) -> dict:
        state = self._get_agent_state(agent_id)
        plan_id = state.current_plan.get("id") if state.current_plan else None

        reflection = await self._reflection_engine.reflect(
            agent_id=agent_id,
            decision_id=decision_id,
            plan_id=plan_id,
            expected_outcome=expected_outcome,
            actual_outcome=actual_outcome,
            success=success,
            cost_actual=cost,
            reward_actual=reward,
        )

        state.total_reflections += 1
        self._reflection_count += 1

        if state.current_plan:
            self._planning_engine.evaluate_plan(
                state.current_plan,
                {"success": success, "actual_cost": cost, "actual_reward": reward},
            )

        await self._broadcast_sse({
            "type": "reflection_completed",
            "data": reflection,
        })

        return reflection

    async def get_decisions(self, agent_id: str, limit: int = 50, offset: int = 0) -> list[dict]:
        return await self._decision_store.get_agent_decisions(agent_id, limit, offset)

    async def get_plans(self, agent_id: str) -> list[dict]:
        state = self._get_agent_state(agent_id)
        plans = []
        if state.current_plan:
            plans.append(state.current_plan)
        return plans

    async def get_reflections(self, agent_id: str, limit: int = 20) -> list[dict]:
        return await self._reflection_engine.get_reflections(agent_id, limit)

    async def get_reasoning_history(self, agent_id: str, limit: int = 30) -> dict:
        decisions = await self._decision_store.get_agent_decisions(agent_id, limit=limit)
        reflections = await self._reflection_engine.get_reflections(agent_id, limit=limit)
        success_rate = await self._reflection_engine.get_success_rate(agent_id)
        lessons = await self._reflection_engine.get_lessons_summary(agent_id)
        plans = await self.get_plans(agent_id)
        state = self._get_agent_state(agent_id)

        return {
            "decisions": decisions,
            "reflections": reflections,
            "plans": plans,
            "success_rate": success_rate,
            "lessons_learned": lessons,
            "stats": {
                "total_decisions": state.total_decisions,
                "total_reflections": state.total_reflections,
                "current_status": state.reasoning_status,
                "provider_used": state.provider_used,
                "last_reasoning_duration_ms": state.last_reasoning_duration_ms,
            },
            "queue_stats": self._queue.get_stats(),
        }

    async def replay(self, agent_id: str, decision_id: str) -> dict:
        decision = await self._decision_store.get(decision_id)
        if not decision:
            return {"error": "Decision not found"}
        if decision["agent_id"] != agent_id:
            return {"error": "Decision does not belong to this agent"}

        return {
            "decision": decision,
            "replayed_at": time.time(),
        }

    async def search_decisions(self, agent_id: str, query: str) -> list[dict]:
        return await self._decision_store.search(agent_id, query)

    async def handle_simulation_event(self, event: SimEvent) -> None:
        if event.event_type == EventType.AGENT_WORKING:
            agent_id = event.payload.get("agent_id", "")
            if agent_id:
                await self.trigger_decision(
                    agent_id, "task_acceptance",
                    context_data={"event": event.to_dict()},
                    priority=4,
                )

        elif event.event_type == EventType.AGENT_IDLE:
            agent_id = event.payload.get("agent_id", "")
            reason = event.payload.get("reason", "")
            if agent_id and reason == "energy_restored":
                await self.trigger_decision(
                    agent_id, "goal_selection",
                    context_data={"event": event.to_dict()},
                    priority=6,
                )

        elif event.event_type == EventType.DAILY_RESET:
            day = event.payload.get("day", 0)
            if self._sim_engine:
                for agent in self._sim_engine.agents:
                    if agent.id in self._agent_states:
                        state = self._agent_states[agent.id]
                        if state.current_plan and state.current_plan.get("status") == "active":
                            state.current_plan = self._planning_engine.advance_plan(state.current_plan)

    def get_agent_reasoning_state(self, agent_id: str) -> dict:
        state = self._get_agent_state(agent_id)
        return {
            "agent_id": agent_id,
            "current_decision": state.current_decision,
            "current_plan": state.current_plan,
            "reasoning_status": state.reasoning_status,
            "total_decisions": state.total_decisions,
            "total_reflections": state.total_reflections,
            "provider_used": state.provider_used,
            "last_reasoning_duration_ms": state.last_reasoning_duration_ms,
        }

    def get_full_state(self) -> dict:
        return {
            "running": self._running,
            "provider": self.get_provider_info(),
            "queue_stats": self._queue.get_stats(),
            "total_decisions": self._decision_count,
            "total_reflections": self._reflection_count,
            "total_events": self._event_count,
            "agent_count": len(self._agent_states),
        }

    async def _processing_loop(self) -> None:
        try:
            while self._running:
                task = await self._queue.process_next(self._process_task)
                if not task:
                    await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("reasoning_loop_error: %s", exc)

    async def _process_task(self, task: ReasoningTask) -> dict:
        return await self.reason(
            task.agent_id,
            task.trigger_type,
            task.context,
        )

    async def _build_context(self, agent_id: str, trigger_type: str, extra: dict) -> dict:
        context = {}

        if self._sim_engine and agent_id in self._sim_engine.profiles:
            profile = self._sim_engine.profiles[agent_id]
            context["identity"] = profile.identity
            context["personality"] = profile.personality
            context["goal"] = profile.goal
            context["skills"] = profile.skills
            context["agent"] = profile.agent.to_dict()
            context["relationships"] = []

        context["simulation_time"] = extra.get("simulation_time", {})
        context["recent_events"] = extra.get("recent_events", [])
        context["constraints"] = {
            "budget": context.get("agent", {}).get("wallet_balance", 0),
            "energy": context.get("agent", {}).get("energy", 50),
            "reputation": context.get("agent", {}).get("reputation", 0),
        }

        return context

    def _get_agent_state(self, agent_id: str) -> AgentReasoningState:
        if agent_id not in self._agent_states:
            self._agent_states[agent_id] = AgentReasoningState(agent_id=agent_id)
        return self._agent_states[agent_id]

    def subscribe_sse(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._sse_subscribers.append(q)
        return q

    def unsubscribe_sse(self, q: asyncio.Queue) -> None:
        if q in self._sse_subscribers:
            self._sse_subscribers.remove(q)

    async def _broadcast_sse(self, data: dict) -> None:
        dead = []
        for q in self._sse_subscribers:
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self._sse_subscribers.remove(q)


reasoning_engine = ReasoningEngine()
