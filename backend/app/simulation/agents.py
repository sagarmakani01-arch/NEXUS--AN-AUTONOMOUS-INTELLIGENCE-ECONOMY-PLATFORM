from __future__ import annotations

import json
import logging
import random
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.simulation")

PROFESSIONS = [
    ("Software Engineer", "technology", ["Python", "JavaScript", "System Design"]),
    ("Data Scientist", "analytics", ["Machine Learning", "Statistics", "Python"]),
    ("Financial Analyst", "finance", ["Quantitative Analysis", "Risk Assessment", "Excel"]),
    ("Marketing Manager", "marketing", ["SEO", "Content Strategy", "Analytics"]),
    ("Legal Counsel", "legal", ["Contract Law", "Compliance", "Negotiation"]),
    ("Architect", "design", ["AutoCAD", "Urban Planning", "Sustainability"]),
    ("Doctor", "healthcare", ["Diagnostics", "Surgery", "Patient Care"]),
    ("Teacher", "education", ["Curriculum Design", "Public Speaking", "Mentoring"]),
    ("Journalist", "media", ["Investigative Reporting", "Writing", "Interviewing"]),
    ("Chef", "hospitality", ["Cuisine", "Menu Design", "Kitchen Management"]),
    ("Pilot", "transportation", ["Navigation", "Aviation Safety", "Flight Planning"]),
    ("Mechanical Engineer", "engineering", ["CAD", "Thermodynamics", "Robotics"]),
    ("Biotech Researcher", "science", ["Genomics", "Lab Techniques", "Data Analysis"]),
    ("Cybersecurity Analyst", "technology", ["Pen Testing", "Network Security", "Forensics"]),
    ("Urban Planner", "government", ["Zoning", "GIS", "Public Policy"]),
    ("Pharmacist", "healthcare", ["Drug Interactions", "Compounding", "Regulations"]),
    ("Graphic Designer", "creative", ["UI/UX", "Illustration", "Typography"]),
    ("Supply Chain Manager", "logistics", ["Procurement", "Forecasting", "ERP"]),
    ("Psychologist", "healthcare", ["CBT", "Assessment", "Research"]),
    ("Environmental Scientist", "science", ["Climate Modeling", "Field Research", "GIS"]),
]

FIRST_NAMES = [
    "Atlas", "Nova", "Cipher", "Echo", "Pulse", "Drift", "Zen", "Apex", "Flux", "Volt",
    "Orion", "Nexus", "Helix", "Vega", "Axiom", "Bolt", "Core", "Haze", "Ion", "Prism",
    "Rift", "Sage", "Tera", "Umbra", "Vox", "Wren", "Zephyr", "Aria", "Blaze", "Chroma",
    "Dusk", "Ember", "Forge", "Gale", "Hawk", "Iris", "Jade", "Kite", "Luna", "Mesa",
    "Neon", "Opal", "Pike", "Quartz", "Raven", "Sol", "Thorn", "Unity", "Wisp", "Yara",
    "Ash", "Beacon", "Cedar", "Dawn", "Eve", "Fern", "Glenn", "Heath", "Ivy", "Juniper",
    "Knot", "Lark", "Moss", "Nest", "Oak", "Pine", "Reed", "Sage", "Thyme", "Vale",
    "Wren", "Yew", "Alder", "Birch", "Coral", "Dune", "Elm", "Flint", "Glen", "Hill",
    "Ilex", "Jasper", "Kelp", "Lava", "Marsh", "Nook", "Oasis", "Peak", "Ridge", "Slade",
    "Tarn", "Upland", "Wood", "Yard", "Zone", "Anchor", "Bridge", "Cliff", "Delta", "Estuary",
]

GOALS = [
    "Maximize quarterly output",
    "Complete certification program",
    "Build professional network",
    "Launch side project",
    "Optimize daily workflow",
    "Mentor junior team members",
    "Research new methodology",
    "Secure client contract",
    "Improve public speaking",
    "Develop proprietary tool",
    "Achieve performance targets",
    "Collaborate on cross-team initiative",
    "Contribute to open-source project",
    "Prepare industry presentation",
    "Streamline operations process",
]


@dataclass
class SimAgent:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    profession: str = ""
    profession_category: str = ""
    skills: list[str] = field(default_factory=list)
    personality: dict = field(default_factory=dict)
    current_status: str = "idle"
    energy: float = 100.0
    reputation: float = 0.0
    wallet_balance: float = 100.0
    current_goal: str = ""
    state_duration: int = 0
    total_work_done: int = 0
    tasks_completed: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "profession": self.profession,
            "profession_category": self.profession_category,
            "skills": self.skills,
            "personality": self.personality,
            "current_status": self.current_status,
            "energy": round(self.energy, 1),
            "reputation": round(self.reputation, 2),
            "wallet_balance": round(self.wallet_balance, 2),
            "current_goal": self.current_goal,
            "state_duration": self.state_duration,
            "total_work_done": self.total_work_done,
            "tasks_completed": self.tasks_completed,
        }


def generate_personality() -> dict:
    return {
        "openness": round(random.uniform(0.1, 1.0), 2),
        "conscientiousness": round(random.uniform(0.1, 1.0), 2),
        "extraversion": round(random.uniform(0.1, 1.0), 2),
        "agreeableness": round(random.uniform(0.1, 1.0), 2),
        "neuroticism": round(random.uniform(0.1, 1.0), 2),
    }


def create_agent(index: int) -> SimAgent:
    prof = random.choice(PROFESSIONS)
    name = f"{FIRST_NAMES[index % len(FIRST_NAMES)]}-{index + 1}"
    return SimAgent(
        name=name,
        profession=prof[0],
        profession_category=prof[1],
        skills=random.sample(prof[2], k=random.randint(1, len(prof[2]))),
        personality=generate_personality(),
        current_status="idle",
        energy=round(random.uniform(60, 100), 1),
        reputation=round(random.uniform(0, 2.0), 2),
        wallet_balance=round(random.uniform(50, 500), 2),
        current_goal=random.choice(GOALS),
    )


def create_agents(count: int = 100) -> list[SimAgent]:
    return [create_agent(i) for i in range(count)]


def tick_agent(agent: SimAgent, hour: int) -> tuple[str, dict] | None:
    if agent.energy <= 0:
        if agent.current_status != "resting":
            agent.current_status = "resting"
            agent.state_duration = 0
            return ("resting", {"reason": "energy_depleted"})

    if agent.current_status == "resting":
        agent.energy = min(100.0, agent.energy + random.uniform(8, 15))
        agent.state_duration += 1
        if agent.energy >= 80:
            agent.current_status = "idle"
            agent.state_duration = 0
            return ("idle", {"reason": "energy_restored"})
        return None

    if agent.current_status == "idle":
        if random.random() < 0.15:
            agent.current_status = "searching"
            agent.state_duration = 0
            return ("searching", {"goal": agent.current_goal})
        agent.energy = max(0, agent.energy - random.uniform(0.2, 0.8))
        return None

    if agent.current_status == "searching":
        agent.energy = max(0, agent.energy - random.uniform(0.5, 1.5))
        agent.state_duration += 1
        efficiency = agent.personality.get("conscientiousness", 0.5)
        find_chance = 0.12 + efficiency * 0.08
        if random.random() < find_chance or agent.state_duration > 8:
            agent.current_status = "working"
            agent.state_duration = 0
            return ("working", {"goal": agent.current_goal})
        if agent.state_duration > 12:
            agent.current_status = "idle"
            agent.state_duration = 0
            return ("idle", {"reason": "search_timeout"})
        return None

    if agent.current_status == "working":
        agent.energy = max(0, agent.energy - random.uniform(1.0, 3.0))
        agent.state_duration += 1
        work_duration = random.randint(4, 10)
        if agent.state_duration >= work_duration:
            completed = random.random() < 0.7
            if completed:
                reward = random.uniform(5, 50)
                agent.wallet_balance += reward
                agent.reputation += random.uniform(0.01, 0.05)
                agent.tasks_completed += 1
                agent.total_work_done += 1
                agent.current_status = "idle"
                agent.state_duration = 0
                return ("idle", {"completed": True, "reward": round(reward, 2)})
            else:
                agent.current_status = "searching"
                agent.state_duration = 0
                agent.reputation = max(0, agent.reputation - 0.01)
                return ("searching", {"completed": False})
        return None

    return None
