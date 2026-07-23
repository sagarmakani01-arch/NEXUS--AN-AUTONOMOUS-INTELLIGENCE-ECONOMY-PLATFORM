import json

from app.reality.persistence import reality_db
from app.domain.models.virtual import InteractionLog


class InteractionHandler:
    """Handles user interactions with the 3D world."""

    async def handle_query(self, user_id: str, query: str, target_type: str = None, target_id: str = None) -> dict:
        log = InteractionLog(
            user_id=user_id, interaction_type="query",
            target_type=target_type, target_id=target_id,
            query=query,
        )

        response = self._generate_response(query, target_type)

        log.response = response
        await reality_db.log_interaction(log)

        return {"query": query, "response": response, "target_type": target_type}

    async def handle_observation(self, user_id: str, target_type: str, target_id: str) -> dict:
        log = InteractionLog(
            user_id=user_id, interaction_type="observe",
            target_type=target_type, target_id=target_id,
            query=f"Observe {target_type} {target_id}",
        )

        info = self._get_target_info(target_type, target_id)
        log.response = json.dumps(info)
        await reality_db.log_interaction(log)

        return {"observation": info}

    async def handle_command(self, user_id: str, command: str, params: dict = None) -> dict:
        log = InteractionLog(
            user_id=user_id, interaction_type="command",
            query=command, response=json.dumps(params or {}),
        )
        await reality_db.log_interaction(log)

        command_map = {
            "follow": "Now following the specified entity.",
            "goto": "Navigating to the specified location.",
            "show": "Displaying requested information.",
            "replay": "Starting historical replay.",
        }
        return {"command": command, "message": command_map.get(command, "Command received.")}

    def _generate_response(self, query: str, target_type: str = None) -> str:
        if "largest" in query.lower() and "research" in query.lower():
            return "The largest research center is located in the northern district. It spans 5 floors with 200 researchers."
        if "most influential" in query.lower() or "scientist" in query.lower():
            return "Dr. Elara Voss from the Institute of Advanced Sciences has the highest influence rating. She has published 47 papers."
        if "economic" in query.lower() and ("region" in query.lower() or "change" in query.lower()):
            return "This region has seen 12% GDP growth this year, driven by technology sector expansion."
        return f"I can see the {target_type or 'area'} you're looking at. The simulation is progressing normally."

    def _get_target_info(self, target_type: str, target_id: str) -> dict:
        base = {"id": target_id, "type": target_type}
        if target_type == "building":
            base.update({
                "company": "Nova Robotics",
                "employees": 3200,
                "founded": "Year 240",
                "specialization": "AI Systems",
            })
        elif target_type == "citizen":
            base.update({
                "name": "Unknown",
                "occupation": "Researcher",
                "skills": ["AI", "Quantum Computing", "Data Analysis"],
                "reputation": 85,
            })
        return base

    async def get_history(self, user_id: str, limit: int = 20) -> list[dict]:
        logs = await reality_db.get_interactions(user_id, limit)
        return [{"type": l.interaction_type, "target": l.target_type, "query": l.query, "time": l.created_at.isoformat() if l.created_at else None} for l in logs]


interaction_handler = InteractionHandler()
