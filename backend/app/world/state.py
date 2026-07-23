import json
import logging
import math
import random
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger("nexus.world")

WORLD_WIDTH = 200
WORLD_HEIGHT = 200
TILE_SIZE = 32

ZONE_TYPES = {
    "residential": {"color": "#4a90d9", "label": "Residential"},
    "commercial": {"color": "#e8a838", "label": "Commercial"},
    "industrial": {"color": "#8b5e3c", "label": "Industrial"},
    "research": {"color": "#7c3aed", "label": "Research"},
    "government": {"color": "#dc2626", "label": "Government"},
    "park": {"color": "#22c55e", "label": "Park"},
    "education": {"color": "#06b6d4", "label": "Education"},
    "financial": {"color": "#f59e0b", "label": "Financial"},
    "medical": {"color": "#ef4444", "label": "Medical"},
    "transport": {"color": "#6b7280", "label": "Transport"},
}

BUILDING_TYPES = {
    "home": {"zone": "residential", "width": 2, "height": 2, "capacity": 4, "color": "#3b82f6"},
    "office": {"zone": "commercial", "width": 3, "height": 3, "capacity": 20, "color": "#f59e0b"},
    "factory": {"zone": "industrial", "width": 4, "height": 3, "capacity": 50, "color": "#78350f"},
    "lab": {"zone": "research", "width": 3, "height": 3, "capacity": 15, "color": "#7c3aed"},
    "university": {"zone": "education", "width": 5, "height": 4, "capacity": 200, "color": "#0891b2"},
    "government_office": {"zone": "government", "width": 4, "height": 3, "capacity": 30, "color": "#dc2626"},
    "hospital": {"zone": "medical", "width": 4, "height": 4, "capacity": 100, "color": "#ef4444"},
    "bank": {"zone": "financial", "width": 2, "height": 2, "capacity": 10, "color": "#eab308"},
    "market": {"zone": "commercial", "width": 3, "height": 2, "capacity": 50, "color": "#f97316"},
    "library": {"zone": "education", "width": 3, "height": 3, "capacity": 30, "color": "#06b6d4"},
    "park_area": {"zone": "park", "width": 6, "height": 6, "capacity": 100, "color": "#22c55e"},
    "station": {"zone": "transport", "width": 3, "height": 2, "capacity": 200, "color": "#6b7280"},
}


@dataclass
class WorldBuilding:
    id: str
    building_type: str
    name: str
    x: int
    y: int
    width: int
    height: int
    capacity: int
    color: str
    zone: str
    employees: list[str] = field(default_factory=list)
    visitors: list[str] = field(default_factory=list)
    current_activity: str = "idle"

    def to_dict(self) -> dict:
        return {
            "id": self.id, "type": self.building_type, "name": self.name,
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "capacity": self.capacity, "color": self.color, "zone": self.zone,
            "employee_count": len(self.employees), "visitor_count": len(self.visitors),
            "activity": self.current_activity,
        }


@dataclass
class WorldZone:
    id: str
    zone_type: str
    x: int
    y: int
    width: int
    height: int
    color: str
    label: str

    def to_dict(self) -> dict:
        return {
            "id": self.id, "type": self.zone_type,
            "x": self.x, "y": self.y, "width": self.width, "height": self.height,
            "color": self.color, "label": self.label,
        }


@dataclass
class WorldRoad:
    id: str
    x1: int
    y1: int
    x2: int
    y2: int
    width: int = 2

    def to_dict(self) -> dict:
        return {"id": self.id, "x1": self.x1, "y1": self.y1,
                "x2": self.x2, "y2": self.y2, "width": self.width}


class WorldState:
    def __init__(self):
        self.width = WORLD_WIDTH
        self.height = WORLD_HEIGHT
        self.tile_size = TILE_SIZE
        self.buildings: list[WorldBuilding] = []
        self.zones: list[WorldZone] = []
        self.roads: list[WorldRoad] = []
        self.citizen_positions: dict[str, dict] = {}
        self.events: list[dict] = []
        self.time_state = {
            "day": 1, "hour": 8, "minute": 0,
            "speed": 1, "paused": False,
            "total_ticks": 0,
        }
        self._generated = False

    def generate_world(self):
        if self._generated:
            return
        self._generate_zones()
        self._generate_roads()
        self._generate_buildings()
        self._generated = True
        logger.info("World generated: %d zones, %d roads, %d buildings",
                     len(self.zones), len(self.roads), len(self.buildings))

    def _generate_zones(self):
        zone_layout = [
            ("residential", 5, 5, 40, 35),
            ("residential", 5, 45, 40, 35),
            ("commercial", 50, 5, 35, 30),
            ("commercial", 50, 40, 35, 30),
            ("industrial", 90, 5, 40, 35),
            ("industrial", 90, 45, 40, 35),
            ("research", 5, 85, 35, 30),
            ("education", 45, 85, 30, 30),
            ("government", 80, 85, 25, 25),
            ("park", 110, 85, 30, 30),
            ("financial", 135, 5, 25, 25),
            ("medical", 135, 35, 25, 25),
            ("transport", 165, 5, 30, 20),
        ]
        for zt, x, y, w, h in zone_layout:
            info = ZONE_TYPES.get(zt, ZONE_TYPES["residential"])
            self.zones.append(WorldZone(
                id=str(uuid.uuid4()), zone_type=zt,
                x=x, y=y, width=w, height=h,
                color=info["color"], label=info["label"],
            ))

    def _generate_roads(self):
        h_roads = [42, 78, 118]
        v_roads = [48, 88, 133, 163]
        for y in h_roads:
            self.roads.append(WorldRoad(id=str(uuid.uuid4()), x1=0, y1=y, x2=200, y2=y, width=3))
        for x in v_roads:
            self.roads.append(WorldRoad(id=str(uuid.uuid4()), x1=x, y1=0, x2=x, y2=200, width=3))

    def _generate_buildings(self):
        building_plans = [
            ("home", "Maple House", 8, 8), ("home", "Oak Residence", 15, 10),
            ("home", "Pine Home", 25, 12), ("home", "Cedar House", 35, 8),
            ("home", "Elm Residence", 10, 50), ("home", "Birch Home", 20, 55),
            ("home", "Willow House", 30, 48), ("home", "Aspen Home", 38, 52),
            ("office", "TechCorp HQ", 55, 10), ("office", "DataFlow Inc", 65, 15),
            ("office", "CloudBase", 72, 8),
            ("factory", "MegaFactory", 95, 10), ("factory", "SteelWorks", 110, 15),
            ("lab", "AI Research Lab", 10, 90), ("lab", "Quantum Lab", 22, 95),
            ("university", "NEXUS University", 50, 92),
            ("government_office", "City Hall", 85, 90),
            ("hospital", "Central Hospital", 140, 40),
            ("bank", "Global Bank", 140, 10), ("bank", "CryptoVault", 148, 15),
            ("market", "Grand Market", 55, 45), ("market", "Tech Bazaar", 65, 50),
            ("library", "Public Library", 50, 100),
            ("park_area", "Central Park", 115, 90),
            ("station", "Main Station", 170, 10),
        ]
        for btype, name, x, y in building_plans:
            info = BUILDING_TYPES.get(btype, BUILDING_TYPES["home"])
            self.buildings.append(WorldBuilding(
                id=str(uuid.uuid4()), building_type=btype, name=name,
                x=x, y=y, width=info["width"], height=info["height"],
                capacity=info["capacity"], color=info["color"], zone=info["zone"],
            ))

    def add_building(self, building_type: str, name: str, x: int, y: int) -> dict:
        info = BUILDING_TYPES.get(building_type, BUILDING_TYPES["home"])
        b = WorldBuilding(
            id=str(uuid.uuid4()), building_type=building_type, name=name,
            x=x, y=y, width=info["width"], height=info["height"],
            capacity=info["capacity"], color=info["color"], zone=info["zone"],
        )
        self.buildings.append(b)
        return b.to_dict()

    def update_citizen_position(self, agent_id: str, x: float, y: float,
                                destination: str | None = None,
                                status: str = "idle",
                                building_id: str | None = None,
                                thought: str | None = None):
        self.citizen_positions[agent_id] = {
            "x": round(x, 1), "y": round(y, 1),
            "destination": destination, "status": status,
            "building_id": building_id, "thought": thought,
        }

    def remove_citizen(self, agent_id: str):
        self.citizen_positions.pop(agent_id, None)

    def add_event(self, event_type: str, description: str, x: float = 0, y: float = 0,
                  entities: list[str] | None = None):
        import time
        self.events.append({
            "type": event_type, "description": description,
            "x": x, "y": y, "entities": entities or [],
            "timestamp": time.time(),
        })
        if len(self.events) > 200:
            self.events = self.events[-100:]

    def tick_time(self, minutes: int = 1):
        if self.time_state["paused"]:
            return
        speed = self.time_state["speed"]
        total = minutes * speed
        self.time_state["minute"] += total
        while self.time_state["minute"] >= 60:
            self.time_state["minute"] -= 60
            self.time_state["hour"] += 1
        while self.time_state["hour"] >= 24:
            self.time_state["hour"] -= 24
            self.time_state["day"] += 1
        self.time_state["total_ticks"] += 1

    def get_map_state(self) -> dict:
        return {
            "width": self.width, "height": self.height,
            "tile_size": self.tile_size,
            "zones": [z.to_dict() for z in self.zones],
            "roads": [r.to_dict() for r in self.roads],
            "buildings": [b.to_dict() for b in self.buildings],
        }

    def get_citizens_state(self, visible_only: bool = True,
                           camera_x: float = 0, camera_y: float = 0,
                           view_width: float = 100, view_height: float = 100) -> list[dict]:
        if not visible_only:
            return [{"agent_id": k, **v} for k, v in self.citizen_positions.items()]
        result = []
        for agent_id, pos in self.citizen_positions.items():
            if (camera_x - 10 <= pos["x"] <= camera_x + view_width + 10 and
                    camera_y - 10 <= pos["y"] <= camera_y + view_height + 10):
                result.append({"agent_id": agent_id, **pos})
        return result

    def get_events_state(self, limit: int = 50) -> list[dict]:
        return self.events[-limit:]

    def get_time_state(self) -> dict:
        return self.time_state.copy()

    def get_full_state(self) -> dict:
        return {
            "map": self.get_map_state(),
            "time": self.get_time_state(),
            "citizen_count": len(self.citizen_positions),
            "event_count": len(self.events),
        }

    def get_nearby_buildings(self, x: float, y: float, radius: float = 20) -> list[dict]:
        result = []
        for b in self.buildings:
            bx = b.x + b.width / 2
            by = b.y + b.height / 2
            dist = math.sqrt((bx - x) ** 2 + (by - y) ** 2)
            if dist <= radius:
                result.append({**b.to_dict(), "distance": round(dist, 1)})
        result.sort(key=lambda b: b["distance"])
        return result


world_state = WorldState()
