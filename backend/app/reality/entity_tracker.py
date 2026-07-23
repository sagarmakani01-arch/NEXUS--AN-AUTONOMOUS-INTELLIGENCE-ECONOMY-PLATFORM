import json
import random

from app.reality.persistence import reality_db
from app.domain.models.virtual import VirtualEntity


class EntityTracker:
    """Tracks citizen positions and activities in the virtual world."""

    ACTIVITIES = ["walking", "working", "shopping", "studying", "meeting", "resting", "exploring", "researching"]

    async def update_position(self, agent_id: str, name: str, x: float, z: float, activity: str = "idle") -> dict:
        entity = await reality_db.get_entity_by_agent(agent_id)
        if entity:
            entity.pos_x = x
            entity.pos_z = z
            entity.activity = activity
            entity.target_x = x + random.uniform(-5, 5)
            entity.target_z = z + random.uniform(-5, 5)
            entity.speed = random.uniform(0.5, 2.0)
            saved = await reality_db.save_entity(entity)
        else:
            region_x = int(x // 100)
            region_z = int(z // 100)
            entity = VirtualEntity(
                region_id=f"r_{region_x}_{region_z}",
                simulation_agent_id=agent_id,
                name=name, entity_type="citizen",
                pos_x=x, pos_z=z,
                target_x=x + random.uniform(-5, 5),
                target_z=z + random.uniform(-5, 5),
                speed=random.uniform(0.5, 2.0),
                activity=activity,
                avatar_data=json.dumps({
                    "color": f"#{random.randint(0, 0xffffff):06x}",
                    "size": random.choice(["small", "medium", "large"]),
                    "profession_icon": random.choice(["⚙", "🔬", "📚", "🏛", "💰"]),
                }),
            )
            saved = await reality_db.save_entity(entity)

        return {
            "id": saved.id, "name": saved.name, "x": saved.pos_x, "z": saved.pos_z,
            "target_x": saved.target_x, "target_z": saved.target_z,
            "activity": saved.activity, "speed": saved.speed,
        }

    async def tick_movement(self) -> int:
        entities = await reality_db.get_entities()
        moved = 0
        for e in entities:
            dx = e.target_x - e.pos_x
            dz = e.target_z - e.pos_z
            dist = (dx * dx + dz * dz) ** 0.5
            if dist > 1:
                step = min(e.speed, dist)
                e.pos_x += (dx / max(dist, 0.01)) * step
                e.pos_z += (dz / max(dist, 0.01)) * step
                moved += 1
            else:
                e.target_x = e.pos_x + random.uniform(-10, 10)
                e.target_z = e.pos_z + random.uniform(-10, 10)
                e.activity = random.choice(self.ACTIVITIES)
            await reality_db.save_entity(e)
        return moved

    async def get_entities_in_range(self, cx: float, cz: float, radius: float = 50.0) -> list[dict]:
        all_entities = await reality_db.get_entities()
        result = []
        for e in all_entities:
            dist = ((e.pos_x - cx) ** 2 + (e.pos_z - cz) ** 2) ** 0.5
            if dist <= radius:
                result.append({
                    "id": e.id, "name": e.name, "type": e.entity_type,
                    "x": e.pos_x, "y": e.pos_y, "z": e.pos_z,
                    "target_x": e.target_x, "target_z": e.target_z,
                    "activity": e.activity, "speed": e.speed,
                })
        return result

    async def follow_entity(self, agent_id: str) -> Optional[dict]:
        entity = await reality_db.get_entity_by_agent(agent_id)
        if not entity:
            return None
        return {
            "id": entity.id, "name": entity.name,
            "x": entity.pos_x, "z": entity.pos_z,
            "activity": entity.activity,
            "target_x": entity.target_x, "target_z": entity.target_z,
        }


entity_tracker = EntityTracker()
