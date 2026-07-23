import asyncio
import logging
import random
from datetime import datetime, timezone

from app.communication.messaging import messaging_system
from app.communication.social_graph import social_graph
from app.communication.trust import trust_system
from app.communication.knowledge import knowledge_exchange
from app.communication.communities import communities_system
from app.communication.intelligence import communication_intelligence
from app.communication import persistence as comm_db

logger = logging.getLogger("nexus.communication.engine")


class CommunicationEngine:
    def __init__(self):
        self.running = False
        self._task: asyncio.Task | None = None
        self._tick_interval = 45.0
        self.messaging = messaging_system
        self.social_graph = social_graph
        self.trust = trust_system
        self.knowledge = knowledge_exchange
        self.communities = communities_system
        self.intelligence = communication_intelligence
        self.stats = {
            "total_ticks": 0,
            "messages_generated": 0,
            "interactions_processed": 0,
            "communities_active": 0,
        }
        self._initialized = False

    async def start(self) -> None:
        if self.running:
            return
        self.running = True
        if not self._initialized:
            await self._initialize_communication_system()
            self._initialized = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("communication_engine_started")

    async def stop(self) -> None:
        self.running = False
        if self._task:
            self._task.cancel()
            self._task = None
        logger.info("communication_engine_stopped")

    async def _initialize_communication_system(self) -> None:
        try:
            existing_communities = await self.communities.list_communities()
            if not existing_communities:
                default_communities = [
                    ("Developers Guild", "Community for software developers and engineers", "open", "technology"),
                    ("Research Network", "Collaborative research and knowledge sharing", "open", "research"),
                    ("Business Alliance", "Professional business networking", "closed", "finance"),
                    ("Innovation Hub", "Cutting-edge technology and innovation", "open", "technology"),
                    ("Marketplace Traders", "Trading and commerce discussions", "open", "retail"),
                ]
                for name, desc, ctype, industry in default_communities:
                    await self.communities.create_community(
                        name=name, description=desc,
                        community_type=ctype, industry=industry,
                    )
                logger.info("initialized_default_communities count=%d", len(default_communities))
        except Exception as exc:
            logger.error("init_communication_error: %s", exc)

    async def _run_loop(self) -> None:
        try:
            while self.running:
                await self._tick()
                await asyncio.sleep(self._tick_interval)
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("communication_loop_error: %s", exc)
            self.running = False

    async def _tick(self) -> None:
        self.stats["total_ticks"] += 1
        try:
            await self._generate_agent_interactions()
            await self._process_community_activity()
            self._update_stats()
        except Exception as exc:
            logger.error("communication_tick_error: %s", exc)

    async def _generate_agent_interactions(self) -> None:
        try:
            from app.simulation.engine import engine as sim_engine
            if not sim_engine.agents or len(sim_engine.agents) < 2:
                return

            num_interactions = min(5, len(sim_engine.agents) // 10)
            for _ in range(num_interactions):
                if random.random() > 0.3:
                    continue
                a, b = random.sample(sim_engine.agents, 2)
                interaction_type = random.choice([
                    "collaboration", "knowledge_share", "positive_outcome",
                    "reliability", "conflict", "unreliability",
                ])
                await self.trust.process_interaction(
                    a.id, "agent", b.id, "agent", interaction_type,
                )
                self.stats["interactions_processed"] += 1

                if random.random() > 0.7:
                    msg_type = random.choice(["private", "team"])
                    topics = [
                        "Project update", "Quick question", "Meeting scheduled",
                        "Great work on the last task", "Need help with something",
                        "Marketplace opportunity", "New skill learned",
                    ]
                    await self.messaging.send_message(
                        sender_id=a.id, sender_type="agent",
                        receiver_id=b.id, receiver_type="agent",
                        content=random.choice(topics),
                        message_type=msg_type,
                    )
                    self.stats["messages_generated"] += 1

        except Exception as exc:
            logger.error("generate_interactions_error: %s", exc)

    async def _process_community_activity(self) -> None:
        try:
            from app.simulation.engine import engine as sim_engine
            if not sim_engine.agents:
                return

            communities = await self.communities.list_communities()
            self.stats["communities_active"] = len(communities)

            if random.random() > 0.1 or not communities:
                return

            agent = random.choice(sim_engine.agents)
            community = random.choice(communities)
            result = await self.communities.join_community(community["id"], agent.id, "agent")
            if result.get("status") == "joined":
                logger.info("agent_joined_community agent=%s community=%s", agent.name, community["name"])

            if random.random() > 0.5:
                knowledge_types = ["skill", "experience", "best_practice", "technical"]
                await self.knowledge.share_knowledge(
                    owner_id=agent.id, owner_type="agent",
                    knowledge_type=random.choice(knowledge_types),
                    title=f"Knowledge from {agent.name}",
                    content=f"Sharing experience and insights from working in the simulation.",
                    visibility=random.choice(["team", "public"]),
                )

        except Exception as exc:
            logger.error("community_activity_error: %s", exc)

    def _update_stats(self) -> None:
        self.stats["messages_generated"] = self.messaging.stats.get("messages_sent", 0)
        self.stats["interactions_processed"] = self.trust.stats.get("trust_updates", 0)

    async def get_agent_communication_state(self, agent_id: str) -> dict:
        inbox = await self.messaging.get_entity_inbox(agent_id)
        social = await self.social_graph.get_network(agent_id)
        knowledge = await self.knowledge.get_entity_knowledge(agent_id)
        social_intel = await self.intelligence.get_agent_social_intelligence(agent_id)
        communities = await self.communities.get_entity_communities(agent_id)
        trust_overview = await self.trust.get_entity_trust_overview(agent_id)

        return {
            "inbox": inbox,
            "social_network": social,
            "knowledge": knowledge,
            "social_intelligence": social_intel,
            "communities": communities,
            "trust_overview": trust_overview,
        }

    def get_state(self) -> dict:
        return {
            "running": self.running,
            "stats": self.stats.copy(),
            "tick_interval": self._tick_interval,
            "messaging": self.messaging.get_state(),
            "social_graph": self.social_graph.get_state(),
            "trust": self.trust.get_state(),
            "knowledge": self.knowledge.get_state(),
            "communities": self.communities.get_state(),
            "intelligence": self.intelligence.get_state(),
        }


communication_engine = CommunicationEngine()
