from __future__ import annotations

import logging
import random
from typing import Any

from app.execution import persistence as ep

logger = logging.getLogger("nexus.execution.collaboration")


class MultiAgentCollaboration:
    async def create_team(self, project_id: str, agent_ids: list[str], roles: dict[str, str] | None = None) -> dict:
        team = {
            "project_id": project_id,
            "members": [],
            "status": "forming",
            "leader_id": agent_ids[0] if agent_ids else None,
        }
        for agent_id in agent_ids:
            role = roles.get(agent_id, "member") if roles else "member"
            caps = await ep.get_capabilities(agent_id)
            team["members"].append({
                "agent_id": agent_id,
                "role": role,
                "capabilities": [c["skill_name"] for c in caps],
                "status": "assigned",
                "tasks_completed": 0,
            })
        team["status"] = "active"
        logger.info("team_created project=%s members=%d", project_id, len(agent_ids))
        return team

    async def assign_team_tasks(self, project_id: str, tasks: list[dict], team: dict) -> dict[str, str]:
        assignments = {}
        member_caps = {}
        for member in team["members"]:
            caps = await ep.get_capabilities(member["agent_id"])
            member_caps[member["agent_id"]] = {c["skill_name"]: c["proficiency"] for c in caps}

        for task in tasks:
            task_skills = task.get("required_skills", [])
            best_agent = None
            best_score = -1
            for member in team["members"]:
                if member["agent_id"] in assignments.values():
                    continue
                caps = member_caps.get(member["agent_id"], {})
                score = sum(caps.get(s, 0) for s in task_skills) / max(len(task_skills), 1)
                if score > best_score:
                    best_score = score
                    best_agent = member["agent_id"]
            if best_agent:
                assignments[task["id"]] = best_agent
                await ep.update_execution_task(task["id"], agent_id=best_agent, status="assigned")
        return assignments

    async def get_team_status(self, team: dict) -> dict:
        member_details = []
        for member in team["members"]:
            tasks = await ep.list_execution_tasks(agent_id=member["agent_id"], status="completed")
            in_progress = await ep.list_execution_tasks(agent_id=member["agent_id"], status="running")
            member_details.append({
                **member,
                "completed_tasks": len(tasks),
                "active_tasks": len(in_progress),
            })
        return {
            "project_id": team.get("project_id"),
            "status": team.get("status"),
            "leader_id": team.get("leader_id"),
            "members": member_details,
            "total_members": len(member_details),
        }

    async def coordinate_handoff(self, from_agent: str, to_agent: str, task_id: str, context: str = "") -> dict:
        task = await ep.get_execution_task(task_id)
        if not task:
            return {"error": "Task not found"}
        await ep.update_execution_task(task_id, agent_id=to_agent, status="assigned")
        logger.info("task_handoff task=%s from=%s to=%s", task_id, from_agent, to_agent)
        return {
            "task_id": task_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "context": context,
            "task_state": task,
        }

    def calculate_team_compatibility(self, agent_caps: list[list[str]]) -> float:
        all_skills = set()
        for caps in agent_caps:
            all_skills.update(caps)
        if not all_skills:
            return 0.0
        coverage = len(all_skills) / 10
        overlaps = 0
        pairs = 0
        for i in range(len(agent_caps)):
            for j in range(i + 1, len(agent_caps)):
                overlap = len(set(agent_caps[i]) & set(agent_caps[j]))
                overlaps += overlap
                pairs += 1
        avg_overlap = overlaps / max(pairs, 1)
        diversity = 1.0 - min(avg_overlap / 5, 1.0)
        return round(min(coverage * 0.6 + diversity * 0.4, 1.0), 3)


collaboration = MultiAgentCollaboration()
