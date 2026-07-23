from __future__ import annotations

import json
import logging
import random
import time
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.identity")

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

LAST_NAMES = [
    "Zero", "One", "Prime", "Nexus", "Core", "Sync", "Byte", "Node", "Link", "Arc",
    "Wave", "Drift", "Flux", "Pulse", "Signal", "Phase", "Shift", "Spark", "Edge", "Vex",
    "Knox", "Vale", "Rift", "Haze", "Glow", "Dusk", "Dawn", "Frost", "Ember", "Ash",
    "Stone", "Steel", "Iron", "Gold", "Swift", "Bright", "Dark", "Free", "Bold", "True",
    "Cross", "Bridge", "Hill", "Peak", "Ridge", "Cliff", "Ford", "Marsh", "Glen", "Vale",
]

PROFESSIONS_DATA = [
    ("Software Engineer", "technology", ["Python", "JavaScript", "System Design", "Docker", "Git"]),
    ("Data Scientist", "analytics", ["Machine Learning", "Statistics", "Python", "R", "SQL"]),
    ("Financial Analyst", "finance", ["Quantitative Analysis", "Risk Assessment", "Excel", "Modeling"]),
    ("Marketing Manager", "marketing", ["SEO", "Content Strategy", "Analytics", "Branding"]),
    ("Legal Counsel", "legal", ["Contract Law", "Compliance", "Negotiation", "Research"]),
    ("Architect", "design", ["AutoCAD", "Urban Planning", "Sustainability", "3D Modeling"]),
    ("Doctor", "healthcare", ["Diagnostics", "Surgery", "Patient Care", "Research"]),
    ("Teacher", "education", ["Curriculum Design", "Public Speaking", "Mentoring", "Assessment"]),
    ("Journalist", "media", ["Investigative Reporting", "Writing", "Interviewing", "Editing"]),
    ("Chef", "hospitality", ["Cuisine", "Menu Design", "Kitchen Management", "Creativity"]),
    ("Pilot", "transportation", ["Navigation", "Aviation Safety", "Flight Planning", "Crisis Mgmt"]),
    ("Mechanical Engineer", "engineering", ["CAD", "Thermodynamics", "Robotics", "Materials"]),
    ("Biotech Researcher", "science", ["Genomics", "Lab Techniques", "Data Analysis", "Writing"]),
    ("Cybersecurity Analyst", "technology", ["Pen Testing", "Network Security", "Forensics", "SIEM"]),
    ("Urban Planner", "government", ["Zoning", "GIS", "Public Policy", "Community Eng"]),
    ("Pharmacist", "healthcare", ["Drug Interactions", "Compounding", "Regulations", "Counseling"]),
    ("Graphic Designer", "creative", ["UI/UX", "Illustration", "Typography", "Motion"]),
    ("Supply Chain Manager", "logistics", ["Procurement", "Forecasting", "ERP", "Analytics"]),
    ("Psychologist", "healthcare", ["CBT", "Assessment", "Research", "Empathy"]),
    ("Environmental Scientist", "science", ["Climate Modeling", "Field Research", "GIS", "Policy"]),
    ("Project Manager", "management", ["Agile", "Risk Mgmt", "Leadership", "Scheduling"]),
    ("Network Engineer", "technology", ["CCNA", "TCP/IP", "Firewalls", "Cloud"]),
    ("Civil Engineer", "engineering", ["Structural", "Surveying", "Concrete", "AutoCAD"]),
    ("Content Writer", "creative", ["Copywriting", "SEO", "Research", "Storytelling"]),
    ("UX Researcher", "design", ["User Testing", "Analytics", "Prototyping", "Empathy"]),
]

GOALS = [
    ("Earn more compute credits", "financial", 500),
    ("Improve reputation score", "social", 80),
    ("Learn a new programming language", "skill", 3),
    ("Join a company", "social", 1),
    ("Complete five jobs", "career", 5),
    ("Become a team lead", "career", 1),
    ("Build a professional network", "social", 10),
    ("Achieve expert skill level", "skill", 1),
    ("Save 1000 NXC", "financial", 1000),
    ("Mentor a junior agent", "social", 1),
    ("Launch a side project", "career", 1),
    ("Complete certification", "skill", 1),
    ("Reach reputation 5.0", "social", 500),
    ("Work on 10 different tasks", "career", 10),
    ("Build trust with 5 agents", "social", 5),
]

SKILL_POOL = [
    "Python", "JavaScript", "Rust", "Go", "SQL", "Docker", "Kubernetes",
    "Machine Learning", "Statistics", "Finance", "Marketing", "Design",
    "Writing", "Leadership", "Negotiation", "Research", "Analytics",
    "Project Management", "Public Speaking", "Networking", "Security",
    "Cloud", "DevOps", "Data Engineering", "UI/UX",
]


def generate_personality_traits() -> dict[str, float]:
    base = random.uniform(30, 70)
    return {
        "curiosity": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
        "creativity": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
        "reliability": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
        "risk_tolerance": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
        "patience": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
        "leadership": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
        "cooperation": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
        "learning_speed": round(max(0, min(100, base + random.uniform(-25, 25))), 1),
    }


def create_identity_data(generation: int = 1) -> dict:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    display = f"{first} {last}"
    prof = random.choice(PROFESSIONS_DATA)
    personality = generate_personality_traits()

    skill_count = random.randint(2, 5)
    chosen_skills = random.sample(SKILL_POOL, k=skill_count)
    skills = []
    for s in chosen_skills:
        level = random.randint(1, 3)
        xp = random.randint(0, 30)
        skills.append({
            "skill_name": s,
            "level": level,
            "experience": xp,
            "max_experience": level * 100,
            "learning_progress": round(xp / (level * 100) * 100, 1),
        })

    goal = random.choice(GOALS)

    return {
        "first_name": first,
        "last_name": last,
        "display_name": display,
        "generation": generation,
        "profession": prof[0],
        "profession_category": prof[1],
        "profession_skills": prof[2],
        "personality": personality,
        "skills": skills,
        "goal": {
            "title": goal[0],
            "category": goal[1],
            "target": goal[2],
            "progress": 0,
        },
        "trust_score": round(random.uniform(40, 80), 1),
    }
