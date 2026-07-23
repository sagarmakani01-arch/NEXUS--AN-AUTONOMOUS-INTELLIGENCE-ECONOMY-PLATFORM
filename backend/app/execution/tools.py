from __future__ import annotations

import json
import logging
import random
import time
from typing import Any

from app.execution import persistence as ep

logger = logging.getLogger("nexus.execution.tools")

BUILTIN_TOOLS = [
    {
        "name": "code_executor",
        "description": "Execute Python code snippets and scripts",
        "tool_type": "code_execution",
        "required_permission": "basic",
        "cost_per_use": 1,
        "input_schema": json.dumps({"code": "string", "language": "string"}),
        "output_schema": json.dumps({"result": "string", "error": "string|null"}),
    },
    {
        "name": "web_search",
        "description": "Search the web for information and resources",
        "tool_type": "web_search",
        "required_permission": "basic",
        "cost_per_use": 2,
        "input_schema": json.dumps({"query": "string", "num_results": "integer"}),
        "output_schema": json.dumps({"results": "array"}),
    },
    {
        "name": "file_manager",
        "description": "Create, read, update, and delete files in workspace",
        "tool_type": "file_management",
        "required_permission": "basic",
        "cost_per_use": 1,
        "input_schema": json.dumps({"action": "string", "path": "string", "content": "string"}),
        "output_schema": json.dumps({"success": "boolean", "content": "string"}),
    },
    {
        "name": "data_analyzer",
        "description": "Analyze datasets, generate statistics and visualizations",
        "tool_type": "data_analysis",
        "required_permission": "basic",
        "cost_per_use": 3,
        "input_schema": json.dumps({"data": "array", "analysis_type": "string"}),
        "output_schema": json.dumps({"statistics": "object", "insights": "array"}),
    },
    {
        "name": "simulation_access",
        "description": "Access and interact with the NEXUS simulation environment",
        "tool_type": "simulation",
        "required_permission": "advanced",
        "cost_per_use": 5,
        "input_schema": json.dumps({"action": "string", "params": "object"}),
        "output_schema": json.dumps({"result": "object"}),
    },
    {
        "name": "communication",
        "description": "Send messages and collaborate with other agents",
        "tool_type": "communication",
        "required_permission": "basic",
        "cost_per_use": 1,
        "input_schema": json.dumps({"recipient": "string", "message": "string", "channel": "string"}),
        "output_schema": json.dumps({"sent": "boolean", "response": "string"}),
    },
    {
        "name": "api_client",
        "description": "Make HTTP requests to external APIs",
        "tool_type": "api_access",
        "required_permission": "advanced",
        "cost_per_use": 2,
        "input_schema": json.dumps({"method": "string", "url": "string", "headers": "object", "body": "object"}),
        "output_schema": json.dumps({"status": "integer", "data": "object"}),
    },
    {
        "name": "document_generator",
        "description": "Generate reports, documentation, and structured documents",
        "tool_type": "document",
        "required_permission": "basic",
        "cost_per_use": 2,
        "input_schema": json.dumps({"template": "string", "data": "object", "format": "string"}),
        "output_schema": json.dumps({"document": "string", "path": "string"}),
    },
    {
        "name": "test_runner",
        "description": "Run test suites and validate code quality",
        "tool_type": "testing",
        "required_permission": "basic",
        "cost_per_use": 2,
        "input_schema": json.dumps({"test_type": "string", "target": "string", "config": "object"}),
        "output_schema": json.dumps({"passed": "integer", "failed": "integer", "report": "string"}),
    },
    {
        "name": "deployment_manager",
        "description": "Deploy applications and services to production",
        "tool_type": "deployment",
        "required_permission": "admin",
        "cost_per_use": 10,
        "input_schema": json.dumps({"service": "string", "environment": "string", "config": "object"}),
        "output_schema": json.dumps({"deployed": "boolean", "url": "string"}),
    },
]


class ToolSystem:
    def __init__(self) -> None:
        self._initialized = False

    async def ensure_tools(self) -> None:
        if self._initialized:
            return
        existing = await ep.list_tools()
        existing_names = {t["name"] for t in existing}
        for tool_def in BUILTIN_TOOLS:
            if tool_def["name"] not in existing_names:
                await ep.create_tool(**tool_def)
        self._initialized = True

    async def list_tools(self, tool_type: str = "") -> list[dict]:
        await self.ensure_tools()
        return await ep.list_tools(tool_type=tool_type)

    async def get_tool(self, tool_id: str) -> dict | None:
        return await ep.get_tool(tool_id)

    async def get_tool_by_name(self, name: str) -> dict | None:
        tools = await ep.list_tools()
        return next((t for t in tools if t["name"] == name), None)

    async def execute_tool(self, tool_name: str, agent_id: str, params: dict) -> dict:
        tool = await self.get_tool_by_name(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        if tool["status"] != "active":
            return {"error": f"Tool '{tool_name}' is not active"}

        start_time = time.time()
        result = await self._simulate_tool(tool_name, params, agent_id)
        duration = time.time() - start_time

        new_uses = tool["total_uses"] + 1
        new_avg_time = (tool["avg_execution_time"] * tool["total_uses"] + duration) / new_uses
        success = "error" not in result
        total = tool["total_uses"] + 1
        old_successes = int(tool["success_rate"] * tool["total_uses"])
        new_success_rate = (old_successes + (1 if success else 0)) / total

        await ep.update_tool(
            tool["id"],
            total_uses=new_uses,
            avg_execution_time=round(new_avg_time, 3),
            success_rate=round(new_success_rate, 2),
        )

        logger.info("tool_executed tool=%s agent=%s success=%s duration=%.3f", tool_name, agent_id, success, duration)
        return {**result, "tool_id": tool["id"], "duration": round(duration, 3), "cost": tool["cost_per_use"]}

    async def _simulate_tool(self, tool_name: str, params: dict, agent_id: str) -> dict:
        if tool_name == "code_executor":
            return {"result": f"Code executed successfully. Output: {random.randint(1, 100)}", "error": None}
        elif tool_name == "web_search":
            query = params.get("query", "general")
            return {"results": [
                {"title": f"Result for '{query}'", "url": f"https://example.com/{query}", "snippet": "Relevant information found"},
                {"title": f"Guide on '{query}'", "url": f"https://docs.example.com/{query}", "snippet": "Comprehensive documentation"},
            ]}
        elif tool_name == "file_manager":
            action = params.get("action", "read")
            path = params.get("path", "/default.txt")
            if action == "create":
                return {"success": True, "content": f"File created at {path}"}
            elif action == "read":
                return {"success": True, "content": f"Content of {path}: sample data"}
            return {"success": True, "content": f"File {action} on {path}"}
        elif tool_name == "data_analyzer":
            return {"statistics": {"mean": 42.5, "std": 12.3, "count": 100}, "insights": ["Strong positive correlation found", "Outliers detected at 95th percentile"]}
        elif tool_name == "communication":
            return {"sent": True, "response": "Message received and acknowledged"}
        elif tool_name == "document_generator":
            return {"document": "Document generated successfully", "path": f"/workspace/docs/{params.get('template', 'report')}.md"}
        elif tool_name == "test_runner":
            total = random.randint(10, 50)
            passed = random.randint(int(total * 0.7), total)
            return {"passed": passed, "failed": total - passed, "report": f"Tests completed: {passed}/{total} passed"}
        else:
            return {"result": f"Tool '{tool_name}' executed with params: {list(params.keys())}"}


tool_system = ToolSystem()
