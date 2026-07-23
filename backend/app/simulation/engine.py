from __future__ import annotations

import asyncio
import json
import logging
import random
import time
import uuid
from dataclasses import dataclass, field

from app.simulation.agents import SimAgent, create_agent, tick_agent
from app.simulation.events import EventQueue, EventType, SimEvent, SimSpeed, SimState
from app.simulation.identity import create_identity_data
from app.simulation.persistence import (
    load_all_identities,
    load_goal,
    load_memories,
    load_personality,
    load_relationships,
    load_skills,
    load_timeline,
    save_goal,
    save_identity,
    save_memory,
    save_personality,
    save_relationship,
    save_skills,
    save_timeline_event,
    update_relationship_on_interaction,
)
from app.simulation.world import World

logger = logging.getLogger("nexus.simulation")


@dataclass
class AgentProfile:
    agent: SimAgent
    identity: dict
    personality: dict
    goal: dict
    skills: list[dict]
    trust_score: float = 50.0

    def to_dict(self) -> dict:
        return {
            "agent": self.agent.to_dict(),
            "identity": self.identity,
            "personality": self.personality,
            "goal": self.goal,
            "skills": self.skills,
            "trust_score": self.trust_score,
        }


class SimulationEngine:
    def __init__(self) -> None:
        self.state = SimState.IDLE
        self.speed = SimSpeed.X1
        self.agents: list[SimAgent] = []
        self.profiles: dict[str, AgentProfile] = {}
        self.event_queue = EventQueue()
        self.world = World(self.event_queue)
        self._task: asyncio.Task | None = None
        self._sse_subscribers: list[asyncio.Queue] = []
        self._lock = asyncio.Lock()
        self._tick_interval = 1.0
        self._started_at: float | None = None
        self._paused_at: float | None = None
        self._total_paused_duration: float = 0
        self._interaction_pairs_seen: set[tuple[str, str]] = set()

    @property
    def uptime_seconds(self) -> float:
        if not self._started_at:
            return 0
        if self._paused_at:
            return self._paused_at - self._started_at - self._total_paused_duration
        return time.time() - self._started_at - self._total_paused_duration

    def _calculate_interval(self) -> float:
        return 1.0 / self.speed.value

    async def _broadcast_sse(self, data: dict) -> None:
        dead = []
        for q in self._sse_subscribers:
            try:
                q.put_nowait(data)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            self._sse_subscribers.remove(q)

    async def _on_event(self, event: SimEvent) -> None:
        self.world.state.total_events += 1
        await self._broadcast_sse({"type": "event", "data": event.to_dict()})

    async def _persist_agent(self, agent: SimAgent) -> None:
        profile = self.profiles.get(agent.id)
        if not profile:
            return
        try:
            await save_skills(agent.id, profile.skills)
            await save_goal(agent.id, profile.goal)
        except Exception as exc:
            logger.error("persist_agent_error agent=%s err=%s", agent.id, exc)

    async def _init_from_db(self) -> None:
        try:
            identities = await load_all_identities()
            if not identities:
                logger.info("no_persisted_identities found")
                return
            loaded = 0
            for agent_id, ident in identities.items():
                personality = await load_personality(agent_id)
                goal = await load_goal(agent_id)
                skills = await load_skills(agent_id)
                if not personality or not goal:
                    continue
                agent = SimAgent(
                    id=agent_id,
                    name=ident.get("display_name", agent_id),
                    current_status="idle",
                    energy=random.uniform(60, 100),
                    reputation=random.uniform(0, 2),
                    wallet_balance=random.uniform(50, 500),
                    current_goal=goal.get("title", ""),
                )
                profile = AgentProfile(
                    agent=agent,
                    identity=ident,
                    personality=personality,
                    goal=goal,
                    skills=skills,
                    trust_score=random.uniform(40, 80),
                )
                self.agents.append(agent)
                self.profiles[agent_id] = profile
                loaded += 1
            logger.info("loaded_identities count=%d", loaded)
        except Exception as exc:
            logger.error("init_from_db_error: %s", exc)

    async def start(self) -> None:
        if self.state == SimState.RUNNING:
            return
        async with self._lock:
            if self.state == SimState.PAUSED:
                self.state = SimState.RUNNING
                if self._paused_at:
                    self._total_paused_duration += time.time() - self._paused_at
                    self._paused_at = None
                await self._broadcast_state()
                await self.event_queue.put(SimEvent(EventType.SIMULATION_STARTED, {"action": "resumed"}))
                self._task = asyncio.create_task(self._run_loop())
                return

            if not self.agents:
                await self._init_from_db()

            if not self.agents:
                await self._spawn_agents(100)
            else:
                for agent in self.agents:
                    if agent.id not in self.profiles:
                        ident_data = create_identity_data()
                        self.profiles[agent.id] = AgentProfile(
                            agent=agent,
                            identity=ident_data,
                            personality=ident_data["personality"],
                            goal={"title": ident_data["goal"]["title"], "category": ident_data["goal"]["category"], "progress": 0, "target": ident_data["goal"]["target"]},
                            skills=ident_data["skills"],
                            trust_score=ident_data["trust_score"],
                        )

            self.state = SimState.RUNNING
            self._started_at = time.time()
            self._paused_at = None
            self._total_paused_duration = 0
            self.world.update_stats(self.agents)

            from app.reasoning.engine import reasoning_engine
            reasoning_engine._sim_engine = self
            reasoning_engine.init()
            await reasoning_engine.start()

            from app.marketplace.engine import marketplace_engine
            await marketplace_engine.start()

            from app.execution.engine import execution_engine
            await execution_engine.start()

            from app.organization.engine import company_engine
            await company_engine.start()

            from app.communication.engine import communication_engine
            await communication_engine.start()

            from app.economy.engine import economy_engine
            await economy_engine.start()

            from app.governance.engine import governance_engine
            await governance_engine.start()

            from app.evolution.engine import evolution_engine
            await evolution_engine.start()

            from app.research.engine import research_engine
            await research_engine.start()

            from app.federation.engine import federation_engine
            await federation_engine.start()

            from app.culture.engine import culture_engine
            await culture_engine.start()

            from app.technology.engine import technology_engine
            await technology_engine.start()

            from app.planetary.engine import planetary_engine
            await planetary_engine.start()

            from app.temporal.engine import temporal_engine
            await temporal_engine.start()

            from app.meta.engine import meta_engine
            await meta_engine.start()

            from app.platform.engine import platform_engine
            await platform_engine.initialize()

            from app.reality.engine import reality_engine
            await reality_engine.initialize()

            from app.management.engine import mgmt_engine
            await mgmt_engine.initialize()

            from app.genesis.engine import genesis_engine
            await genesis_engine.start()

            from app.compute.engine import compute_engine
            await compute_engine.start()

            from app.discovery.engine import discovery_engine
            await discovery_engine.start()

            from app.world.state import world_state as nexus_world
            nexus_world.generate_world()
            for agent in self.agents:
                await citizen_movement_engine.initialize_citizen(agent.id, agent.name)

            await self._broadcast_state()
            await self.event_queue.put(SimEvent(EventType.SIMULATION_STARTED, {"agent_count": len(self.agents)}))
            self._task = asyncio.create_task(self._run_loop())
            logger.info("simulation_started agents=%d", len(self.agents))

    async def _spawn_agents(self, count: int) -> None:
        for i in range(count):
            agent = create_agent(i)
            ident_data = create_identity_data()
            agent.name = ident_data["display_name"]

            profile = AgentProfile(
                agent=agent,
                identity={
                    "first_name": ident_data["first_name"],
                    "last_name": ident_data["last_name"],
                    "display_name": ident_data["display_name"],
                    "generation": ident_data["generation"],
                    "status": "active",
                    "profession": ident_data["profession"],
                    "profession_category": ident_data["profession_category"],
                },
                personality=ident_data["personality"],
                goal={
                    "title": ident_data["goal"]["title"],
                    "category": ident_data["goal"]["category"],
                    "progress": 0,
                    "target": ident_data["goal"]["target"],
                },
                skills=ident_data["skills"],
                trust_score=ident_data["trust_score"],
            )

            self.agents.append(agent)
            self.profiles[agent.id] = profile

            await save_identity(agent.id, profile.identity)
            await save_personality(agent.id, profile.personality)
            await save_goal(agent.id, profile.goal)
            await save_skills(agent.id, profile.skills)
            await save_timeline_event(agent.id, 1, "Created", f"{agent.name} was born into the simulation")

            from app.resources.manager import resource_manager
            await resource_manager.init_agent(agent.id, initial_balance=agent.wallet_balance)

            await self.event_queue.put(SimEvent(EventType.AGENT_SPAWNED, {
                "agent_id": agent.id,
                "name": agent.name,
                "profession": ident_data["profession"],
            }))

    async def pause(self) -> None:
        if self.state != SimState.RUNNING:
            return
        self.state = SimState.PAUSED
        self._paused_at = time.time()
        if self._task:
            self._task.cancel()
            self._task = None
        from app.marketplace.engine import marketplace_engine
        await marketplace_engine.stop()
        from app.execution.engine import execution_engine
        await execution_engine.stop()
        from app.organization.engine import company_engine
        await company_engine.stop()
        from app.communication.engine import communication_engine
        await communication_engine.stop()
        from app.economy.engine import economy_engine
        await economy_engine.stop()
        from app.governance.engine import governance_engine
        await governance_engine.stop()
        from app.evolution.engine import evolution_engine
        await evolution_engine.stop()
        from app.research.engine import research_engine
        await research_engine.stop()
        from app.federation.engine import federation_engine
        await federation_engine.stop()
        from app.culture.engine import culture_engine
        await culture_engine.stop()
        from app.technology.engine import technology_engine
        await technology_engine.stop()
        from app.planetary.engine import planetary_engine
        await planetary_engine.stop()
        from app.temporal.engine import temporal_engine
        await temporal_engine.stop()
        from app.meta.engine import meta_engine
        await meta_engine.stop()
        await self.event_queue.put(SimEvent(EventType.SIMULATION_PAUSED, {"tick": self.world.state.clock.tick_count}))
        await self._broadcast_state()

    async def reset(self) -> None:
        if self._task:
            self._task.cancel()
            self._task = None
        self.state = SimState.IDLE
        self.agents = []
        self.profiles = {}
        self.event_queue = EventQueue()
        self.world = World(self.event_queue)
        self._started_at = None
        self._paused_at = None
        self._total_paused_duration = 0
        self._interaction_pairs_seen = set()
        await self._broadcast_state()
        await self._broadcast_sse({"type": "reset", "data": {}})

    def set_speed(self, speed: SimSpeed) -> None:
        self.speed = speed
        self._tick_interval = self._calculate_interval()

    async def _run_loop(self) -> None:
        try:
            while self.state == SimState.RUNNING:
                tick_start = time.time()
                await self._tick()
                elapsed = time.time() - tick_start
                sleep_time = max(0, self._tick_interval - elapsed)
                await asyncio.sleep(sleep_time)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("simulation_loop_error: %s", exc)
            self.state = SimState.IDLE

    async def _tick(self) -> None:
        day_rolled = self.world.state.clock.advance(minutes=1)
        current_day = self.world.state.clock.day

        if day_rolled:
            for agent in self.agents:
                agent.energy = min(100.0, agent.energy + 20)
            await self.event_queue.put(SimEvent(EventType.DAILY_RESET, {"day": current_day}))
            for agent in self.agents:
                profile = self.profiles.get(agent.id)
                if profile:
                    await save_timeline_event(agent.id, current_day, "DailyReset", f"Day {current_day} began")

            from app.resources.manager import resource_manager
            agent_ids = [a.id for a in self.agents]
            asyncio.create_task(resource_manager.process_daily(agent_ids))

        from app.world.movement import citizen_movement_engine
        from app.world.state import world_state as nexus_world
        nexus_world.tick_time(1)
        if self.world.state.clock.tick_count % 5 == 0:
            citizen_movement_engine.tick()

        for agent in self.agents:
            result = tick_agent(agent, self.world.state.clock.hour)
            if result:
                new_status, details = result
                profile = self.profiles.get(agent.id)

                if new_status == "working" and profile:
                    await self._on_agent_work_start(agent, profile, current_day)
                elif new_status == "idle" and details.get("completed"):
                    await self._on_agent_work_complete(agent, profile, details, current_day)
                elif new_status == "resting" and profile:
                    await save_memory(agent.id, "physical", "low", "Ran out of energy", f"Agent {agent.name} collapsed from exhaustion")
                    await save_timeline_event(agent.id, current_day, "Resting", "Collapsed from exhaustion, resting to recover")

                event_map = {
                    "working": EventType.AGENT_WORKING,
                    "resting": EventType.AGENT_RESTING,
                    "idle": EventType.AGENT_IDLE,
                    "searching": EventType.AGENT_SEARCHING,
                }
                await self.event_queue.put(SimEvent(event_map.get(new_status, EventType.AGENT_IDLE), {
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "new_status": new_status,
                    **details,
                }))

                from app.reasoning.engine import reasoning_engine
                if new_status == "working":
                    await reasoning_engine.handle_simulation_event(
                        SimEvent(event_map[new_status], {"agent_id": agent.id, **details})
                    )
                elif new_status == "idle" and details.get("reason") == "energy_restored":
                    await reasoning_engine.handle_simulation_event(
                        SimEvent(EventType.AGENT_IDLE, {"agent_id": agent.id, **details})
                    )

        self._maybe_create_relationships()
        self.world.update_stats(self.agents)

        await self.event_queue.put(SimEvent(EventType.SIMULATION_TICK, {
            "clock": self.world.state.clock.to_dict(),
            "population": self.world.state.population,
        }))

        from app.temporal.engine import temporal_engine
        full_state = self.get_full_state()
        await temporal_engine.tick(full_state)

        from app.meta.engine import meta_engine
        await meta_engine.tick(full_state)
        if self.world.state.clock.tick_count % 50 == 0:
            asyncio.create_task(meta_engine.observe(
                simulation_id="nexus_main",
                tick=self.world.state.clock.tick_count,
                year=self.world.state.clock.year,
                world_state=full_state,
            ))

        from app.reality.engine import reality_engine
        asyncio.create_task(reality_engine.tick())

        from app.management.engine import mgmt_engine
        asyncio.create_task(mgmt_engine.tick(agent_count=len(self.agents)))

        from app.genesis.engine import genesis_engine
        if self.world.state.clock.tick_count % 3 == 0:
            asyncio.create_task(genesis_engine.tick())

        from app.compute.engine import compute_engine
        if self.world.state.clock.tick_count % 10 == 0:
            asyncio.create_task(compute_engine.tick())

        from app.discovery.engine import discovery_engine
        asyncio.create_task(discovery_engine.tick(full_state))

        await self._broadcast_sse({"type": "world", "data": full_state})

    async def _on_agent_work_start(self, agent: SimAgent, profile: AgentProfile, day: int) -> None:
        await save_memory(agent.id, "career", "medium", "Started working", f"Working on: {agent.current_goal}")
        await save_timeline_event(agent.id, day, "Working", f"Started task: {agent.current_goal}")

    async def _on_agent_work_complete(self, agent: SimAgent, profile: AgentProfile, details: dict, day: int) -> None:
        reward = details.get("reward", 0)
        goal = profile.goal
        goal["progress"] = min(goal["target"], goal.get("progress", 0) + 1)

        await save_goal(agent.id, goal)
        await save_memory(agent.id, "career", "high", "Completed job", f"Earned {reward} NXC. Progress: {goal['progress']}/{goal['target']}")
        await save_timeline_event(agent.id, day, "JobCompleted", f"Completed a job, earned {reward} NXC")

        from app.resources.manager import resource_manager
        await resource_manager.on_work_completed(agent.id, reward, goal.get("title", ""))

        skills = profile.skills
        if skills:
            sk = random.choice(skills)
            gain = random.randint(5, 15)
            sk["experience"] = min(sk["max_experience"], sk["experience"] + gain)
            if sk["experience"] >= sk["max_experience"]:
                sk["level"] += 1
                sk["max_experience"] = sk["level"] * 100
                sk["experience"] = 0
                await save_timeline_event(agent.id, day, "SkillUp", f"{sk['skill_name']} leveled up to {sk['level']}")
            sk["learning_progress"] = round(sk["experience"] / sk["max_experience"] * 100, 1)
            await save_skills(agent.id, skills)

        if goal["progress"] >= goal["target"]:
            await save_memory(agent.id, "achievement", "high", "Goal completed", f"Completed: {goal['title']}")
            await save_timeline_event(agent.id, day, "GoalCompleted", f"Goal achieved: {goal['title']}")
            new_goals = [
                ("Earn more compute credits", "financial", 500),
                ("Improve reputation score", "social", 80),
                ("Learn a new programming language", "skill", 3),
                ("Complete five jobs", "career", 5),
                ("Build a professional network", "social", 10),
            ]
            g = random.choice(new_goals)
            profile.goal = {"title": g[0], "category": g[1], "progress": 0, "target": g[2]}
            await save_goal(agent.id, profile.goal)

    def _maybe_create_relationships(self) -> None:
        if len(self.agents) < 2:
            return
        if random.random() > 0.05:
            return
        a, b = random.sample(self.agents, 2)
        pair = tuple(sorted([a.id, b.id]))
        if pair in self._interaction_pairs_seen and random.random() > 0.3:
            return
        self._interaction_pairs_seen.add(pair)
        collab = random.random() > 0.3
        asyncio.create_task(self._create_relationship(a.id, b.id, "collaboration" if collab else "conflict"))

    async def _create_relationship(self, agent_a: str, agent_b: str, interaction_type: str) -> None:
        try:
            await update_relationship_on_interaction(agent_a, agent_b, interaction_type)
            profile_a = self.profiles.get(agent_a)
            profile_b = self.profiles.get(agent_b)
            name_a = profile_a.agent.name if profile_a else agent_a
            name_b = profile_b.agent.name if profile_b else agent_b
            await save_memory(agent_a, "social", "medium", f"{interaction_type.title()} with {name_b}", f"Interacted with {name_b}", agent_b)
            await save_memory(agent_b, "social", "medium", f"{interaction_type.title()} with {name_a}", f"Interacted with {name_a}", agent_a)
        except Exception as exc:
            logger.error("relationship_error: %s", exc)

    def get_full_state(self) -> dict:
        from app.reasoning.engine import reasoning_engine
        from app.marketplace.engine import marketplace_engine
        from app.execution.engine import execution_engine
        from app.organization.engine import company_engine
        from app.communication.engine import communication_engine
        from app.economy.engine import economy_engine
        from app.governance.engine import governance_engine
        from app.evolution.engine import evolution_engine
        from app.research.engine import research_engine
        from app.meta.engine import meta_engine
        from app.platform.engine import platform_engine
        from app.reality.engine import reality_engine
        from app.management.engine import mgmt_engine
        from app.genesis.engine import genesis_engine
        from app.compute.engine import compute_engine
        return {
            "state": self.state.value,
            "speed": self.speed.value,
            "world": self.world.to_dict(),
            "uptime": round(self.uptime_seconds, 1),
            "agents_count": len(self.agents),
            "reasoning": reasoning_engine.get_full_state(),
            "marketplace": marketplace_engine.get_state(),
            "execution": execution_engine.get_state(),
            "companies": company_engine.get_state(),
            "communication": communication_engine.get_state(),
            "economy": economy_engine.get_state(),
            "governance": governance_engine.get_state(),
            "evolution": evolution_engine.get_state(),
            "research": research_engine.get_state(),
            "federation": federation_engine.get_state(),
            "culture": culture_engine.get_state(),
            "technology": technology_engine.get_state(),
            "planetary": planetary_engine.get_state(),
            "temporal": {
                "initialized": True,
                "tick_count": self.world.state.clock.tick_count,
            },
            "meta": meta_engine.get_full_state(),
            "platform": platform_engine.get_full_state(),
            "reality": reality_engine.get_full_state(),
            "management": await mgmt_engine.get_full_state(),
            "genesis": await genesis_engine.get_full_state(),
            "compute": await compute_engine.get_full_state(),
            "discovery": await discovery_engine.get_full_state(),
        }

    def get_agents_page(self, page: int = 0, size: int = 20) -> dict:
        start = page * size
        end = start + size
        agents_page = self.agents[start:end]
        enriched = []
        for a in agents_page:
            profile = self.profiles.get(a.id)
            entry = a.to_dict()
            if profile:
                entry["identity"] = profile.identity
                entry["trust_score"] = profile.trust_score
                entry["profession"] = profile.identity.get("profession", "")
                entry["generation"] = profile.identity.get("generation", 1)
                entry["display_name"] = profile.identity.get("display_name", a.name)
            enriched.append(entry)
        return {
            "agents": enriched,
            "total": len(self.agents),
            "page": page,
            "size": size,
            "pages": (len(self.agents) + size - 1) // size,
        }

    async def get_agent_profile(self, agent_id: str) -> dict | None:
        agent = next((a for a in self.agents if a.id == agent_id), None)
        if not agent:
            return None
        profile = self.profiles.get(agent_id)
        memories = await load_memories(agent_id, limit=20)
        timeline = await load_timeline(agent_id)
        relationships = await load_relationships(agent_id)
        rel_profiles = []
        for rel in relationships:
            other_id = rel["other_agent_id"]
            other_profile = self.profiles.get(other_id)
            if other_profile:
                rel["other_name"] = other_profile.identity.get("display_name", other_id)
                rel["other_profession"] = other_profile.identity.get("profession", "")
            rel_profiles.append(rel)

        result = agent.to_dict()
        if profile:
            result["identity"] = profile.identity
            result["personality"] = profile.personality
            result["goal"] = profile.goal
            result["skills"] = profile.skills
            result["trust_score"] = profile.trust_score
        result["memories"] = memories
        result["timeline"] = timeline
        result["relationships"] = rel_profiles

        from app.reasoning.engine import reasoning_engine
        result["reasoning"] = reasoning_engine.get_agent_reasoning_state(agent_id)

        from app.resources.manager import resource_manager
        try:
            result["resources"] = await resource_manager.get_full_state(agent_id)
        except Exception:
            result["resources"] = {}

        from app.marketplace import bidding_engine, contract_manager
        try:
            result["marketplace"] = {
                "proposals": await bidding_engine.get_agent_bids(agent_id),
                "contracts": await contract_manager.list_agent_contracts(agent_id),
                "stats": await contract_manager.get_contract_stats(agent_id),
            }
        except Exception:
            result["marketplace"] = {}

        from app.execution.engine import execution_engine
        try:
            result["execution"] = await execution_engine.get_agent_execution_state(agent_id)
        except Exception:
            result["execution"] = {}

        from app.organization.persistence import get_members
        try:
            from sqlalchemy import select
            from app.core.database import async_session_factory
            from app.domain.models.company import CompanyMember
            async with async_session_factory() as session:
                member_result = await session.execute(
                    select(CompanyMember).where(
                        CompanyMember.agent_id == agent_id,
                        CompanyMember.status == "active",
                    )
                )
                memberships = member_result.scalars().all()
                result["company"] = {
                    "is_employee": len(memberships) > 0,
                    "memberships": [
                        {
                            "company_id": m.company_id,
                            "role": m.role,
                            "department": m.department,
                            "title": m.title,
                            "salary": m.salary,
                        }
                        for m in memberships
                    ],
                }
        except Exception:
            result["company"] = {"is_employee": False, "memberships": []}

        from app.communication.engine import communication_engine
        try:
            result["communication"] = await communication_engine.get_agent_communication_state(agent_id)
        except Exception:
            result["communication"] = {}

        from app.economy.investment import investment_engine
        try:
            result["economy"] = await investment_engine.get_agent_investments(agent_id)
        except Exception:
            result["economy"] = {}

        from app.governance.engine import governance_engine
        try:
            result["governance"] = await governance_engine.get_agent_governance_state(agent_id)
        except Exception:
            result["governance"] = {}

        from app.evolution import persistence as evo_db
        try:
            mentorships = await evo_db.get_mentorships(mentor_id=agent_id)
            mentee_ships = await evo_db.get_mentorships(mentee_id=agent_id)
            innovations = await evo_db.list_innovations(discoverer_id=agent_id)
            result["evolution"] = {
                "mentorships_as_mentor": len(mentorships),
                "mentorships_as_mentee": len(mentee_ships),
                "innovations_count": len(innovations),
                "innovations": innovations[:5],
            }
        except Exception:
            result["evolution"] = {}

        try:
            from app.research import persistence as res_db
            res_projects = await res_db.list_projects(lead_agent_id=agent_id, limit=5)
            res_pubs = await res_db.list_publications()
            agent_pubs = [p for p in res_pubs if agent_id in p.get("authors", [])]
            res_innovations = await res_db.list_research_innovations(discoverer_agent_id=agent_id)
            result["research"] = {
                "projects_led": len(res_projects),
                "publications": len(agent_pubs),
                "innovations": len(res_innovations),
                "recent_projects": res_projects[:3],
            }
        except Exception:
            result["research"] = {}

        return result

    def search_agents(self, query: str = "", profession: str = "", status: str = "", min_reputation: float = 0, generation: int = 0) -> list[dict]:
        results = []
        for a in self.agents:
            profile = self.profiles.get(a.id)
            if not profile:
                continue
            ident = profile.identity
            if query and query.lower() not in ident.get("display_name", "").lower() and query.lower() not in ident.get("first_name", "").lower():
                continue
            if profession and profession.lower() not in ident.get("profession", "").lower():
                continue
            if status and a.current_status != status:
                continue
            if a.reputation < min_reputation:
                continue
            if generation and ident.get("generation", 1) != generation:
                continue
            entry = a.to_dict()
            entry["identity"] = ident
            entry["trust_score"] = profile.trust_score
            entry["profession"] = ident.get("profession", "")
            entry["generation"] = ident.get("generation", 1)
            results.append(entry)
        return results

    def subscribe_sse(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._sse_subscribers.append(q)
        return q

    def unsubscribe_sse(self, q: asyncio.Queue) -> None:
        if q in self._sse_subscribers:
            self._sse_subscribers.remove(q)

    async def _broadcast_state(self) -> None:
        await self._broadcast_sse({"type": "state_change", "data": self.get_full_state()})


engine = SimulationEngine()
