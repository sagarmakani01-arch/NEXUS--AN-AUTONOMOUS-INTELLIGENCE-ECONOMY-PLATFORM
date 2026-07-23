import json
import random
from datetime import datetime

from app.reality.persistence import reality_db
from app.domain.models.virtual import CinematicEvent


class CinematicDirector:
    """Automated storytelling that highlights important events."""

    CINEMATIC_TEMPLATES = [
        {"type": "scientific_breakthrough", "title": "Scientific Breakthrough!", "desc": "A major discovery has been made in the research district.", "priority": 0.9, "duration": 15},
        {"type": "company_founded", "title": "New Company Founded", "desc": "A new enterprise has been established in the commercial zone.", "priority": 0.6, "duration": 10},
        {"type": "economic_milestone", "title": "Economic Milestone", "desc": "The civilization's economy has reached a new peak.", "priority": 0.7, "duration": 12},
        {"type": "political_decision", "title": "Major Decision", "desc": "The governing council has enacted a significant policy change.", "priority": 0.8, "duration": 14},
        {"type": "cultural_event", "title": "Cultural Event", "desc": "A major cultural festival is taking place in the city center.", "priority": 0.5, "duration": 8},
        {"type": "construction_complete", "title": "Construction Complete", "desc": "A major infrastructure project has been completed.", "priority": 0.5, "duration": 10},
    ]

    async def generate_event(self, event_type: str = None) -> dict:
        template = random.choice(self.CINEMATIC_TEMPLATES) if event_type is None else next(
            (t for t in self.CINEMATIC_TEMPLATES if t["type"] == event_type), self.CINEMATIC_TEMPLATES[0]
        )

        cam_pos = {
            "x": random.uniform(-30, 30),
            "y": random.uniform(20, 50),
            "z": random.uniform(-30, 30),
        }
        cam_target = {
            "x": random.uniform(-10, 10),
            "y": 0,
            "z": random.uniform(-10, 10),
        }

        event = CinematicEvent(
            event_type=template["type"],
            title=template["title"],
            description=template["desc"],
            cam_position=json.dumps(cam_pos),
            cam_target=json.dumps(cam_target),
            duration_seconds=template["duration"],
            priority=template["priority"],
        )
        saved = await reality_db.save_cinematic(event)
        return {
            "id": saved.id, "type": saved.event_type, "title": saved.title,
            "description": saved.description, "camera": cam_pos,
            "target": cam_target, "duration": saved.duration_seconds,
            "priority": saved.priority,
        }

    async def get_pending_events(self) -> list[dict]:
        events = await reality_db.get_cinematic_events(triggered=0, limit=10)
        return [{"id": e.id, "type": e.event_type, "title": e.title, "priority": e.priority} for e in events]

    async def trigger_event(self, event_id: str) -> dict:
        event = await reality_db.get_cinematic_events()
        target = next((e for e in event if e.id == event_id), None)
        if not target:
            return {"error": "Event not found"}

        import sqlalchemy as sa
        from app.core.database import async_session_factory
        async with async_session_factory() as session:
            await session.execute(
                sa.update(CinematicEvent).where(CinematicEvent.id == event_id).values(triggered=1)
            )
            await session.commit()

        return {
            "triggered": True,
            "title": target.title,
            "camera": target.cam_position,
            "target": target.cam_target,
            "duration": target.duration_seconds,
        }

    async def get_state(self) -> dict:
        pending = await reality_db.get_cinematic_events(triggered=0)
        triggered = await reality_db.get_cinematic_events(triggered=1)
        return {
            "pending": len(pending),
            "triggered": len(triggered),
            "total": len(pending) + len(triggered),
        }


cinematic_director = CinematicDirector()
