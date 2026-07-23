import logging
import random

from app.evolution import persistence as evo_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.evolution.mentorship")

MENTORSHIP_CONFIG = {
    "max_mentees_per_mentor": 3,
    "max_sessions": 10,
    "quality_decay_rate": 0.05,
    "knowledge_transfer_per_session": 0.15,
    "min_reputation_for_mentoring": 30,
    "match_bonus_reputation": 10,
    "match_bonus_skill_level": 2,
}


class MentorshipEngine:
    def __init__(self):
        self.stats = {
            "mentorships_created": 0,
            "sessions_completed": 0,
            "mentorships_graduated": 0,
        }

    async def find_mentor(self, mentee_id: str, preferred_domain: str | None = None) -> dict | None:
        from app.simulation.engine import engine as sim_engine
        mentee = next((a for a in sim_engine.agents if a.id == mentee_id), None)
        mentee_profile = sim_engine.profiles.get(mentee_id)
        if not mentee or not mentee_profile:
            return None

        mentee_level = sum(s.get("level", 1) for s in mentee_profile.skills) / max(len(mentee_profile.skills), 1)

        candidates = []
        for agent in sim_engine.agents:
            if agent.id == mentee_id:
                continue
            profile = sim_engine.profiles.get(agent.id)
            if not profile:
                continue
            if agent.reputation < MENTORSHIP_CONFIG["min_reputation_for_mentoring"]:
                continue

            mentor_level = sum(s.get("level", 1) for s in profile.skills) / max(len(profile.skills), 1)
            if mentor_level <= mentee_level:
                continue

            skill_match = 0
            if preferred_domain:
                for s in profile.skills:
                    if preferred_domain.lower() in s.get("skill_name", "").lower():
                        skill_match = s.get("level", 1) / 20
                        break

            score = (agent.reputation / 100) * 0.4 + (mentor_level / 20) * 0.3 + skill_match * 0.3
            candidates.append({
                "agent_id": agent.id,
                "name": agent.name,
                "reputation": agent.reputation,
                "skill_level": mentor_level,
                "score": score,
            })

        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates[0] if candidates else None

    async def create_mentorship(self, mentor_id: str, mentee_id: str) -> dict:
        from app.simulation.engine import engine as sim_engine
        mentor_profile = sim_engine.profiles.get(mentor_id)
        mentee_profile = sim_engine.profiles.get(mentee_id)
        if not mentor_profile or not mentee_profile:
            return {"success": False, "error": "Agent not found"}

        existing = await evo_db.get_mentorships(mentor_id=mentor_id, mentee_id=mentee_id, status="active")
        if existing:
            return {"success": False, "error": "Active mentorship exists"}

        mentorship_id = await evo_db.create_mentorship(
            mentor_id=mentor_id, mentee_id=mentee_id,
        )
        self.stats["mentorships_created"] += 1

        await dispatch(Event(EventType.MENTORSHIP_STARTED, {
            "mentorship_id": mentorship_id,
            "mentor_id": mentor_id,
            "mentee_id": mentee_id,
        }))

        return {
            "success": True,
            "mentorship_id": mentorship_id,
            "mentor": mentor_profile.agent.name,
            "mentee": mentee_profile.agent.name,
        }

    async def conduct_session(self, mentorship_id: str) -> dict:
        mentorships = await evo_db.get_mentorships(status="active")
        mentorship = next((m for m in mentorships if m["id"] == mentorship_id), None)
        if not mentorship:
            return {"success": False, "error": "Active mentorship not found"}

        sessions = mentorship.get("sessions_completed", 0)
        if sessions >= MENTORSHIP_CONFIG["max_sessions"]:
            await evo_db.update_mentorship(mentorship_id, status="graduated")
            self.stats["mentorships_graduated"] += 1
            return {"success": True, "status": "graduated", "reason": "Max sessions reached"}

        mentor_id = mentorship["mentor_id"]
        mentee_id = mentorship["mentee_id"]

        from app.simulation.engine import engine as sim_engine
        mentor_profile = sim_engine.profiles.get(mentor_id)
        mentee_profile = sim_engine.profiles.get(mentee_id)
        if not mentor_profile or not mentee_profile:
            return {"success": False, "error": "Agent not found"}

        knowledge_transferred = {}
        for ms in mentor_profile.skills:
            for rs in mentee_profile.skills:
                if ms.get("skill_name") == rs.get("skill_name"):
                    transfer_rate = MENTORSHIP_CONFIG["knowledge_transfer_per_session"]
                    quality = mentorship.get("quality_score", 0.8)
                    transfer = int(ms.get("experience", 0) * transfer_rate * quality)
                    if transfer > 0:
                        rs["experience"] = min(rs.get("max_experience", 100),
                                               rs.get("experience", 0) + transfer)
                        knowledge_transferred[ms["skill_name"]] = transfer
                        break

        new_skills_improved = []
        if random.random() < 0.3:
            improved = random.choice([s["skill_name"] for s in mentee_profile.skills] or ["General"])
            new_skills_improved.append(improved)

        new_sessions = sessions + 1
        quality_change = random.uniform(-0.1, 0.15)
        new_quality = max(0, min(1, mentorship.get("quality_score", 0.8) + quality_change))

        await evo_db.update_mentorship(
            mentorship_id,
            sessions_completed=new_sessions,
            knowledge_transferred=knowledge_transferred,
            skills_improved=new_skills_improved,
            quality_score=round(new_quality, 3),
            duration_days=mentorship.get("duration_days", 0) + 1,
        )
        self.stats["sessions_completed"] += 1

        return {
            "success": True,
            "session_number": new_sessions,
            "knowledge_transferred": knowledge_transferred,
            "skills_improved": new_skills_improved,
            "quality_score": round(new_quality, 3),
        }

    async def get_agent_mentorships(self, agent_id: str) -> dict:
        as_mentor = await evo_db.get_mentorships(mentor_id=agent_id)
        as_mentee = await evo_db.get_mentorships(mentee_id=agent_id)
        return {
            "as_mentor": [m for m in as_mentor],
            "as_mentee": [m for m in as_mentee],
            "total": len(as_mentor) + len(as_mentee),
            "active": len([m for m in as_mentor + as_mentee if m.get("status") == "active"]),
        }

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


mentorship_engine = MentorshipEngine()
