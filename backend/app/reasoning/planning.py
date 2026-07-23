from __future__ import annotations

import logging
import random
import uuid
from datetime import datetime, timezone

logger = logging.getLogger("nexus.reasoning.planning")

GOAL_MILESTONE_TEMPLATES = {
    "financial": [
        {"title": "Assess current financial position", "task_count_range": (1, 2)},
        {"title": "Identify income opportunities", "task_count_range": (1, 3)},
        {"title": "Execute earning strategy", "task_count_range": (1, 3)},
        {"title": "Review and optimize", "task_count_range": (1, 2)},
    ],
    "social": [
        {"title": "Map social landscape", "task_count_range": (1, 2)},
        {"title": "Initiate connections", "task_count_range": (1, 3)},
        {"title": "Build relationships", "task_count_range": (1, 3)},
        {"title": "Strengthen network", "task_count_range": (1, 2)},
    ],
    "skill": [
        {"title": "Assess current skill level", "task_count_range": (1, 2)},
        {"title": "Begin learning phase", "task_count_range": (1, 3)},
        {"title": "Practice and apply", "task_count_range": (1, 3)},
        {"title": "Demonstrate proficiency", "task_count_range": (1, 2)},
    ],
    "career": [
        {"title": "Evaluate career position", "task_count_range": (1, 2)},
        {"title": "Pursue opportunities", "task_count_range": (1, 3)},
        {"title": "Execute career move", "task_count_range": (1, 3)},
        {"title": "Consolidate gains", "task_count_range": (1, 2)},
    ],
    "personal": [
        {"title": "Set personal objectives", "task_count_range": (1, 2)},
        {"title": "Take initial actions", "task_count_range": (1, 3)},
        {"title": "Make progress", "task_count_range": (1, 3)},
        {"title": "Achieve milestone", "task_count_range": (1, 2)},
    ],
}

TASK_TEMPLATES = {
    "financial": [
        "Research available opportunities", "Negotiate terms", "Execute transaction",
        "Monitor returns", "Adjust strategy",
    ],
    "social": [
        "Identify key contacts", "Reach out", "Schedule meeting",
        "Share knowledge", "Offer assistance",
    ],
    "skill": [
        "Study fundamentals", "Complete exercises", "Build project",
        "Seek feedback", "Refine approach",
    ],
    "career": [
        "Update portfolio", "Apply for positions", "Prepare for interviews",
        "Complete onboarding", "Deliver first project",
    ],
    "personal": [
        "Define success criteria", "Take first step", "Build momentum",
        "Overcome obstacle", "Celebrate progress",
    ],
}


class PlanningEngine:
    def create_plan(self, agent_id: str, goal: str, decision_id: str, context: dict) -> dict:
        category = self._detect_goal_category(goal)
        agent = context.get("agent", {})
        personality = context.get("personality", {})
        skills = context.get("skills", [])

        milestones = self._generate_milestones(category, goal, context)

        plan_id = str(uuid.uuid4())
        return {
            "id": plan_id,
            "agent_id": agent_id,
            "decision_id": decision_id,
            "goal": goal,
            "status": "active",
            "milestones": milestones,
            "current_milestone_index": 0,
            "current_task_index": 0,
            "current_action_index": 0,
            "progress": 0.0,
            "evaluation": {},
            "started_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }

    def advance_plan(self, plan: dict) -> dict:
        milestones = plan.get("milestones", [])
        mi = plan.get("current_milestone_index", 0)
        ti = plan.get("current_task_index", 0)
        ai = plan.get("current_action_index", 0)

        if mi >= len(milestones):
            plan["status"] = "completed"
            plan["progress"] = 100.0
            plan["completed_at"] = datetime.now(timezone.utc).isoformat()
            return plan

        milestone = milestones[mi]
        tasks = milestone.get("tasks", [])

        if ti >= len(tasks):
            milestone["completed"] = True
            plan["current_milestone_index"] = mi + 1
            plan["current_task_index"] = 0
            plan["current_action_index"] = 0
            plan["progress"] = self._calc_progress(plan)
            plan["updated_at"] = datetime.now(timezone.utc).isoformat()
            return plan

        task = tasks[ti]
        actions = task.get("actions", [])

        if ai >= len(actions):
            task["completed"] = True
            plan["current_task_index"] = ti + 1
            plan["current_action_index"] = 0
        else:
            actions[ai]["completed"] = True
            plan["current_action_index"] = ai + 1

        plan["progress"] = self._calc_progress(plan)
        plan["updated_at"] = datetime.now(timezone.utc).isoformat()

        all_done = all(
            t.get("completed", False)
            for m in milestones
            for t in m.get("tasks", [])
        )
        if all_done:
            plan["status"] = "completed"
            plan["progress"] = 100.0
            plan["completed_at"] = datetime.now(timezone.utc).isoformat()

        return plan

    def evaluate_plan(self, plan: dict, actual_outcome: dict) -> dict:
        expected = plan.get("evaluation", {})
        actual_cost = actual_outcome.get("actual_cost", 0)
        actual_reward = actual_outcome.get("actual_reward", 0)
        success = actual_outcome.get("success", False)

        expected_cost = 0
        expected_reward = 0
        total_actions = 0
        completed_actions = 0

        for m in plan.get("milestones", []):
            for t in m.get("tasks", []):
                for a in t.get("actions", []):
                    total_actions += 1
                    if a.get("completed"):
                        completed_actions += 1
                    expected_cost += a.get("cost", 0)

        completion_rate = completed_actions / max(total_actions, 1)
        cost_efficiency = 1.0 - min(1.0, abs(actual_cost - expected_cost) / max(expected_cost, 1))
        reward_efficiency = actual_reward / max(expected_reward, 1) if expected_reward > 0 else (1.0 if actual_reward > 0 else 0.0)

        overall_score = (completion_rate * 0.3 + cost_efficiency * 0.3 + reward_efficiency * 0.2 + (1.0 if success else 0.3) * 0.2)

        evaluation = {
            "success": success,
            "completion_rate": round(completion_rate, 3),
            "cost_efficiency": round(cost_efficiency, 3),
            "reward_efficiency": round(reward_efficiency, 3),
            "overall_score": round(overall_score, 3),
            "total_actions": total_actions,
            "completed_actions": completed_actions,
            "actual_cost": actual_cost,
            "actual_reward": actual_reward,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
        plan["evaluation"] = evaluation
        return evaluation

    def replan(self, plan: dict, new_context: dict) -> dict:
        wallet = new_context.get("wallet_balance", 0)
        energy = new_context.get("energy", 50)

        if energy < 20:
            for m in plan.get("milestones", []):
                for t in m.get("tasks", []):
                    for a in t.get("actions", []):
                        if not a.get("completed"):
                            a["estimated_duration"] = int(a.get("estimated_duration", 10) * 1.5)

        if wallet < 10:
            for m in plan.get("milestones", []):
                for t in m.get("tasks", []):
                    for a in t.get("actions", []):
                        if not a.get("completed") and a.get("cost", 0) > wallet:
                            a["cost"] = round(wallet * 0.5, 2)

        plan["updated_at"] = datetime.now(timezone.utc).isoformat()
        return plan

    def _detect_goal_category(self, goal: str) -> str:
        goal_lower = goal.lower()
        if any(w in goal_lower for w in ("earn", "save", "credit", "nxc", "money", "financial")):
            return "financial"
        if any(w in goal_lower for w in ("network", "relationship", "trust", "social", "mentor")):
            return "social"
        if any(w in goal_lower for w in ("learn", "skill", "certification", "study", "level")):
            return "skill"
        if any(w in goal_lower for w in ("job", "career", "hire", "promote", "lead", "work")):
            return "career"
        return "personal"

    def _generate_milestones(self, category: str, goal: str, context: dict) -> list[dict]:
        templates = GOAL_MILESTONE_TEMPLATES.get(category, GOAL_MILESTONE_TEMPLATES["personal"])
        task_pool = TASK_TEMPLATES.get(category, TASK_TEMPLATES["personal"])

        milestones = []
        num_milestones = random.randint(2, min(4, len(templates)))

        for i in range(num_milestones):
            tmpl = templates[i % len(templates)]
            num_tasks = random.randint(*tmpl["task_count_range"])

            tasks = []
            available_tasks = [t for t in task_pool if t not in [tt["title"] for tt in tasks]]
            if not available_tasks:
                available_tasks = task_pool

            for _ in range(num_tasks):
                task_title = random.choice(available_tasks)
                available_tasks = [t for t in available_tasks if t != task_title]

                num_actions = random.randint(1, 3)
                actions = []
                for j in range(num_actions):
                    action_templates = [
                        f"Prepare for {task_title.lower()}",
                        f"Execute {task_title.lower()} step {j+1}",
                        f"Review {task_title.lower()} results",
                    ]
                    actions.append({
                        "id": str(uuid.uuid4())[:8],
                        "title": action_templates[j % len(action_templates)],
                        "estimated_duration": random.randint(5, 30),
                        "cost": round(random.uniform(0, 20), 2),
                        "completed": False,
                    })

                tasks.append({
                    "id": str(uuid.uuid4())[:8],
                    "title": task_title,
                    "actions": actions,
                    "completed": False,
                })

            milestones.append({
                "id": str(uuid.uuid4())[:8],
                "title": tmpl["title"],
                "tasks": tasks,
                "completed": False,
            })

        return milestones

    def _calc_progress(self, plan: dict) -> float:
        total = 0
        completed = 0
        for m in plan.get("milestones", []):
            for t in m.get("tasks", []):
                for _ in t.get("actions", []):
                    total += 1
        mi = plan.get("current_milestone_index", 0)
        ti = plan.get("current_task_index", 0)
        ai = plan.get("current_action_index", 0)
        milestones = plan.get("milestones", [])
        for i, m in enumerate(milestones):
            if i < mi:
                for t in m.get("tasks", []):
                    completed += len(t.get("actions", []))
            elif i == mi:
                tasks = m.get("tasks", [])
                for j, t in enumerate(tasks):
                    if j < ti:
                        completed += len(t.get("actions", []))
                    elif j == ti:
                        completed += ai
        return round((completed / max(total, 1)) * 100, 1)
