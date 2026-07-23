import logging
import random

from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.evolution.skills")

SKILL_HIERARCHY = {
    "Programming": ["Software Development", "System Design", "DevOps", "Data Engineering"],
    "Design": ["UI/UX Design", "Graphic Design", "Product Design", "Brand Development"],
    "Research": ["Data Analysis", "Scientific Writing", "Market Research", "Research Methods"],
    "Business": ["Strategy", "Finance", "Marketing", "Sales", "Operations"],
    "Communication": ["Writing", "Public Speaking", "Negotiation", "Teaching"],
    "Data Science": ["Machine Learning", "Statistical Analysis", "Deep Learning", "NLP"],
    "Management": ["Project Management", "Leadership", "Team Building", "Conflict Resolution"],
    "Creative": ["Content Creation", "Video Production", "Music", "Photography"],
}

SKILL_SYNERGIES = {
    ("Software Development", "Data Analysis"): 0.15,
    ("Machine Learning", "Data Analysis"): 0.20,
    ("Strategy", "Finance"): 0.15,
    ("Writing", "Marketing"): 0.12,
    ("Leadership", "Project Management"): 0.18,
    ("UI/UX Design", "Software Development"): 0.15,
    ("Public Speaking", "Negotiation"): 0.14,
    ("Machine Learning", "Software Development"): 0.16,
}


class SkillInheritanceEngine:
    def __init__(self):
        self.stats = {
            "skills_inherited": 0,
            "skills_mixed": 0,
            "skills_enhanced": 0,
        }

    async def inherit_skills(self, parent_skills: list[dict],
                             parent_reputation: float = 50) -> list[dict]:
        inherited = []
        inherit_chance = 0.5 + (parent_reputation / 200)

        for ps in parent_skills:
            if random.random() < inherit_chance:
                level = max(1, ps.get("level", 1) - random.randint(0, 1))
                experience = ps.get("experience", 0) // 2
                child_skill = {
                    "skill_name": ps.get("skill_name", "Unknown"),
                    "level": level,
                    "experience": experience,
                    "max_experience": ps.get("max_experience", 100),
                    "learning_progress": 0,
                    "certified": False,
                    "inheritance_quality": random.uniform(0.5, 1.0),
                }
                inherited.append(child_skill)
                self.stats["skills_inherited"] += 1

        return inherited

    async def mix_skills(self, skills_a: list[dict], skills_b: list[dict]) -> list[dict]:
        all_skills = {}
        for s in skills_a:
            name = s.get("skill_name", "Unknown")
            all_skills[name] = s

        for s in skills_b:
            name = s.get("skill_name", "Unknown")
            if name in all_skills:
                existing = all_skills[name]
                avg_level = (existing.get("level", 1) + s.get("level", 1)) / 2
                max_exp = max(existing.get("experience", 0), s.get("experience", 0))
                all_skills[name] = {
                    **existing,
                    "level": max(1, round(avg_level)),
                    "experience": max_exp,
                    "mixed_from": "both_parents",
                }
                self.stats["skills_mixed"] += 1
            else:
                all_skills[name] = s

        mixed = list(all_skills.values())
        enhanced = self._apply_synergies(mixed)
        return enhanced

    def _apply_synergies(self, skills: list[dict]) -> list[dict]:
        skill_names = {s.get("skill_name") for s in skills}
        enhanced = skills.copy()

        for (a, b), bonus in SKILL_SYNERGIES.items():
            if a in skill_names and b in skill_names:
                for i, s in enumerate(enhanced):
                    if s.get("skill_name") in (a, b):
                        old_level = enhanced[i].get("level", 1)
                        enhanced[i]["level"] = min(20, old_level + 1)
                        enhanced[i]["synergy_bonus"] = bonus
                        self.stats["skills_enhanced"] += 1

        return enhanced

    async def generate_offspring_skills(self, parent_skills_a: list[dict],
                                        parent_skills_b: list[dict],
                                        parent_rep_a: float = 50,
                                        parent_rep_b: float = 50) -> list[dict]:
        inherited_a = await self.inherit_skills(parent_skills_a, parent_rep_a)
        inherited_b = await self.inherit_skills(parent_skills_b, parent_rep_b)
        combined = await self.mix_skills(inherited_a, inherited_b)

        existing = {s["skill_name"] for s in combined}
        if random.random() < 0.3:
            available = []
            for category, skills_list in SKILL_HIERARCHY.items():
                for sk in skills_list:
                    if sk not in existing:
                        available.append(sk)
            if available:
                new_skill = random.choice(available)
                combined.append({
                    "skill_name": new_skill,
                    "level": 1,
                    "experience": 0,
                    "max_experience": 100,
                    "learning_progress": 0,
                    "certified": False,
                    "innate": True,
                })

        return combined

    def get_skill_tree(self) -> dict:
        return SKILL_HIERARCHY.copy()

    def get_synergies(self) -> list[dict]:
        return [
            {"skill_a": a, "skill_b": b, "bonus": bonus}
            for (a, b), bonus in SKILL_SYNERGIES.items()
        ]

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "total_synergies": len(SKILL_SYNERGIES),
        }


skill_inheritance_engine = SkillInheritanceEngine()
