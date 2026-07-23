from app.platform.persistence import platform_db
from app.domain.models.platform import DeveloperTool


class DeveloperSDK:
    """Provides developer tools, templates, and testing utilities."""

    TOOL_PRESETS = [
        {"name": "Simulation Debugger", "type": "debugger", "endpoint": "/api/v1/platform/debug/simulation", "desc": "Step-through simulation debugger with breakpoints and variable inspection."},
        {"name": "Event Inspector", "type": "inspector", "endpoint": "/api/v1/platform/debug/events", "desc": "Real-time event stream inspector with filtering and search."},
        {"name": "Agent Inspector", "type": "inspector", "endpoint": "/api/v1/platform/debug/agents", "desc": "Detailed agent state inspector with memory, skills, and relationships."},
        {"name": "Timeline Explorer", "type": "explorer", "endpoint": "/api/v1/platform/debug/timeline", "desc": "Interactive timeline browser for debugging simulation history."},
        {"name": "Performance Monitor", "type": "monitor", "endpoint": "/api/v1/platform/debug/performance", "desc": "Real-time performance metrics for simulation engine subsystems."},
        {"name": "API Playground", "type": "testing", "endpoint": "/api/v1/platform/debug/api", "desc": "Interactive API testing environment with request builder and response viewer."},
    ]

    async def init_tools(self) -> list[dict]:
        results = []
        for tool in self.TOOL_PRESETS:
            existing = await platform_db.get_tools(tool["type"])
            if any(t.name == tool["name"] for t in existing):
                continue
            t = DeveloperTool(name=tool["name"], description=tool["desc"], tool_type=tool["type"], endpoint=tool["endpoint"])
            saved = await platform_db.create_tool(t)
            results.append({"id": saved.id, "name": saved.name, "type": saved.tool_type})
        return results

    async def get_tools(self, tool_type: str = None) -> list[dict]:
        tools = await platform_db.get_tools(tool_type)
        return [{"id": t.id, "name": t.name, "description": t.description, "type": t.tool_type, "endpoint": t.endpoint, "enabled": t.enabled} for t in tools]

    async def get_api_documentation(self) -> list[dict]:
        return [
            {"group": "Auth", "endpoints": ["POST /auth/login", "POST /auth/register"]},
            {"group": "Agents", "endpoints": ["GET /agents", "GET /agents/{id}", "GET /agents/search"]},
            {"group": "Economy", "endpoints": ["GET /economy/markets", "POST /economy/invest", "GET /economy/indicators"]},
            {"group": "World", "endpoints": ["GET /world/state", "GET /world/citizens", "GET /world/buildings"]},
            {"group": "Temporal", "endpoints": ["GET /temporal/clock", "POST /temporal/clock/advance", "GET /temporal/history/events"]},
            {"group": "Meta", "endpoints": ["POST /meta/patterns/discover", "POST /meta/experiments/create", "GET /meta/recommendations"]},
        ]


sdk = DeveloperSDK()
