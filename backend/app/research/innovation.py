import json
import logging
import random

from app.research import persistence as db
from app.research.knowledge_graph import knowledge_graph_engine
from app.research.projects import project_manager
from app.research.experiments import experiment_engine
from app.research.publications import publication_engine
from app.research.technology_tree import technology_tree_engine
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.innovation")

INNOVATION_TYPES = {
    "incremental": {"impact_range": (5, 25), "novelty_range": (0.2, 0.5),
                    "description": "Small improvements to existing technologies"},
    "breakthrough": {"impact_range": (30, 80), "novelty_range": (0.7, 1.0),
                     "description": "Major advance that opens new possibilities"},
    "disruptive": {"impact_range": (50, 100), "novelty_range": (0.8, 1.0),
                   "description": "Technology that transforms an entire field"},
    "convergent": {"impact_range": (20, 60), "novelty_range": (0.5, 0.8),
                   "description": "Innovation from combining multiple domains"},
    "emergent": {"impact_range": (10, 40), "novelty_range": (0.6, 0.9),
                 "description": "Unexpected discovery from unrelated research"},
}

SEED_IDEAS = [
    ("Adaptive Neural Architecture", "ai", "A neural network that dynamically restructures itself"),
    ("Quantum Error Correction Protocol", "quantum", "Novel approach to reducing quantum decoherence"),
    ("Bio-Compatible Computing Substrate", "biotech", "Living cells used as computational elements"),
    ("Self-Assembling Nanomaterials", "materials", "Materials that build themselves from molecular components"),
    ("Climate Prediction Engine", "climate", "AI system for ultra-long-range climate forecasting"),
    ("Energy Harvesting Fabric", "energy", "Clothing that generates electricity from body heat"),
    ("Autonomous Research Laboratory", "ai", "AI-driven lab that designs and runs its own experiments"),
    ("Quantum-Secure Communication Network", "quantum", "Unhackable communication using quantum entanglement"),
]


class ResearchInnovationEngine:
    def __init__(self):
        self.stats = {
            "innovations_proposed": 0,
            "innovations_adopted": 0,
            "breakthrough_innovations": 0,
            "ideas_evaluated": 0,
        }

    async def generate_idea(self, discoverer_agent_id: str | None = None,
                            domain: str | None = None) -> dict:
        if not domain and random.random() > 0.5:
            idea = random.choice(SEED_IDEAS)
            title, domain, description = idea
        else:
            domain = domain or random.choice(list(TECH_CATEGORIES.keys()) if 'TECH_CATEGORIES' in dir() else ["ai", "biotech", "materials"])
            title = f"Novel {domain.title()} Innovation"
            description = f"A new approach to {domain} based on recent discoveries"

        innovation_type = random.choice(list(INNOVATION_TYPES.keys()))
        config = INNOVATION_TYPES[innovation_type]

        innovation_id = await db.create_research_innovation(
            title=title, description=description,
            innovation_type=innovation_type, domain=domain,
            novelty_score=round(random.uniform(*config["novelty_range"]), 3),
            impact_score=round(random.uniform(*config["impact_range"]), 3),
            feasibility_score=round(random.uniform(0.3, 0.9), 3),
            discoverer_agent_id=discoverer_agent_id,
        )
        self.stats["innovations_proposed"] += 1
        return {
            "innovation_id": innovation_id, "title": title,
            "type": innovation_type, "domain": domain,
        }

    async def evaluate_idea(self, innovation_id: str) -> dict:
        innovations = await db.list_research_innovations()
        innovation = next((i for i in innovations if i["id"] == innovation_id), None)
        if not innovation:
            return {"success": False, "error": "Innovation not found"}

        self.stats["ideas_evaluated"] += 1

        novelty = innovation.get("novelty_score", 0.5)
        impact = innovation.get("impact_score", 0.5)
        feasibility = innovation.get("feasibility_score", 0.5)

        evaluation_score = novelty * 0.35 + impact * 0.4 + feasibility * 0.25
        recommendation = "adopt" if evaluation_score > 0.6 else "revise" if evaluation_score > 0.4 else "reject"

        return {
            "innovation_id": innovation_id,
            "evaluation_score": round(evaluation_score, 3),
            "recommendation": recommendation,
            "novelty": novelty, "impact": impact, "feasibility": feasibility,
        }

    async def adopt_innovation(self, innovation_id: str) -> dict:
        innovations = await db.list_research_innovations()
        innovation = next((i for i in innovations if i["id"] == innovation_id), None)
        if not innovation:
            return {"success": False, "error": "Innovation not found"}

        await db.update_knowledge_node(innovation_id, status="adopted") if False else None
        self.stats["innovations_adopted"] += 1
        if innovation.get("impact_score", 0) > 70:
            self.stats["breakthrough_innovations"] += 1

        await dispatch(Event(EventType.INNOVATION_DISCOVERED, {
            "innovation_id": innovation_id,
            "title": innovation["title"],
            "type": innovation["innovation_type"],
            "impact": innovation["impact_score"],
        }))
        return {"success": True, "innovation_id": innovation_id}

    async def get_innovations(self, organization_id: str | None = None) -> list[dict]:
        return await db.list_research_innovations(organization_id=organization_id)

    async def get_innovation_stats(self) -> dict:
        return {"stats": self.stats.copy()}

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


from app.research.technology_tree import TECH_CATEGORIES  # noqa: E402


research_innovation_engine = ResearchInnovationEngine()
