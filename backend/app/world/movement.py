import logging
import math
import random

from app.world.state import world_state

logger = logging.getLogger("nexus.world.movement")

CITIZEN_SPEED = 0.3
DESTINATION_THRESHOLD = 2.0

STATUS_ACTIVITIES = {
    "walking": "Walking to destination",
    "working": "Working at office",
    "researching": "Conducting research",
    "shopping": "Shopping at market",
    "meeting": "Meeting with colleague",
    "resting": "Resting at home",
    "studying": "Studying at university",
    "exploring": "Exploring the city",
    "commuting": "Commuting to work",
    "socializing": "Socializing with friends",
}

THOUGHTS = [
    "Thinking about work tasks",
    "Wondering about the economy",
    "Considering a career change",
    "Planning tomorrow's schedule",
    "Reflecting on recent research",
    "Looking for new opportunities",
    "Thinking about lunch",
    "Considering an investment",
    "Planning a meeting",
    "Reviewing recent decisions",
]


class CitizenMovementEngine:
    def __init__(self):
        self.citizen_destinations: dict[str, dict] = {}
        self.stats = {
            "total_moves": 0,
            "total_destinations_reached": 0,
        }

    async def initialize_citizen(self, agent_id: str, name: str | None = None):
        x = random.uniform(5, 40)
        y = random.uniform(5, 40)
        building = random.choice([b for b in world_state.buildings if b.building_type == "home"] or world_state.buildings)
        if building:
            x = building.x + random.uniform(0, building.width)
            y = building.y + random.uniform(0, building.height)

        world_state.update_citizen_position(
            agent_id, x, y, status="resting",
            building_id=building.id if building else None,
            thought="Just woke up",
        )
        self._assign_new_destination(agent_id)

    def _assign_new_destination(self, agent_id: str):
        buildings = world_state.buildings
        if not buildings:
            return

        status_weights = {
            "working": 0.3, "shopping": 0.15, "exploring": 0.2,
            "meeting": 0.1, "resting": 0.15, "researching": 0.1,
        }
        status = random.choices(list(status_weights.keys()),
                                weights=list(status_weights.values()), k=1)[0]

        type_map = {
            "working": ["office", "factory"],
            "shopping": ["market"],
            "exploring": ["park_area", "library"],
            "meeting": ["office", "market", "bank"],
            "resting": ["home"],
            "researching": ["lab", "university"],
        }
        target_types = type_map.get(status, ["home"])
        candidates = [b for b in buildings if b.building_type in target_types]
        if not candidates:
            candidates = buildings

        target = random.choice(candidates)
        dest_x = target.x + random.uniform(0, target.width)
        dest_y = target.y + random.uniform(0, target.height)

        self.citizen_destinations[agent_id] = {
            "x": dest_x, "y": dest_y,
            "building_id": target.id,
            "building_name": target.name,
            "status": status,
            "activity": STATUS_ACTIVITIES.get(status, "Moving"),
            "thought": random.choice(THOUGHTS),
        }

    def tick(self):
        for agent_id, dest in list(self.citizen_destinations.items()):
            pos = world_state.citizen_positions.get(agent_id)
            if not pos:
                continue

            dx = dest["x"] - pos["x"]
            dy = dest["y"] - pos["y"]
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < DESTINATION_THRESHOLD:
                world_state.update_citizen_position(
                    agent_id, dest["x"], dest["y"],
                    status=dest["status"],
                    building_id=dest.get("building_id"),
                    thought=dest.get("thought"),
                )
                self.stats["total_destinations_reached"] += 1
                self._assign_new_destination(agent_id)
            else:
                speed = CITIZEN_SPEED * random.uniform(0.8, 1.2)
                nx = dx / dist
                ny = dy / dist
                new_x = pos["x"] + nx * speed
                new_y = pos["y"] + ny * speed
                world_state.update_citizen_position(
                    agent_id, new_x, new_y,
                    destination=dest.get("building_name"),
                    status="walking",
                    thought=dest.get("thought"),
                )
                self.stats["total_moves"] += 1

    def get_state(self) -> dict:
        return {"stats": self.stats.copy(), "active_destinations": len(self.citizen_destinations)}


citizen_movement_engine = CitizenMovementEngine()
