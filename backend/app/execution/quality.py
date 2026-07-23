from __future__ import annotations

import logging
import random

from app.execution import persistence as ep

logger = logging.getLogger("nexus.execution.quality")


class QualityEvaluation:
    async def evaluate_task(self, task_id: str, agent_id: str, project_id: str) -> dict:
        task = await ep.get_execution_task(task_id)
        if not task:
            return {"error": "Task not found"}

        requirements_met = self._score_requirements(task)
        quality_score = self._score_quality(task, requirements_met)
        errors_count = self._count_errors(task)
        efficiency = self._score_efficiency(task)
        satisfaction = self._score_satisfaction(quality_score, requirements_met)

        result = await ep.create_execution_result(
            task_id=task_id, agent_id=agent_id, project_id=project_id,
            status=task.get("status", "completed"),
            quality_score=quality_score,
            requirements_met=requirements_met,
            errors_count=errors_count,
            efficiency_score=efficiency,
            user_satisfaction=satisfaction,
            deliverables=[task.get("title", "")],
            tools_used=[],
        )

        await ep.update_execution_task(task_id, quality_score=quality_score)
        logger.info("task_evaluated task=%s quality=%.2f", task_id, quality_score)
        return result

    async def evaluate_project(self, project_id: str) -> dict:
        results = await ep.list_execution_results(project_id=project_id)
        if not results:
            return {"project_id": project_id, "avg_quality": 0, "total_tasks": 0}

        completed = [r for r in results if r["status"] == "completed"]
        failed = [r for r in results if r["status"] == "failed"]
        avg_quality = sum(r["quality_score"] for r in results) / len(results)
        avg_satisfaction = sum(r["user_satisfaction"] for r in results) / len(results)
        total_errors = sum(r["errors_count"] for r in results)
        total_cost = sum(r["cost_incurred"] for r in results)

        return {
            "project_id": project_id,
            "total_tasks": len(results),
            "completed": len(completed),
            "failed": len(failed),
            "avg_quality": round(avg_quality, 2),
            "avg_satisfaction": round(avg_satisfaction, 2),
            "total_errors": total_errors,
            "total_cost": round(total_cost, 2),
            "completion_rate": round(len(completed) / max(len(results), 1) * 100, 1),
        }

    def _score_requirements(self, task: dict) -> float:
        base = 0.7
        if task.get("result"):
            base += 0.2
        if task.get("quality_score") and task["quality_score"] > 0.5:
            base += 0.1
        return round(min(base + random.uniform(-0.05, 0.1), 1.0), 2)

    def _score_quality(self, task: dict, requirements_met: float) -> float:
        base = requirements_met * 0.6
        duration_bonus = 0.2 if task.get("actual_duration", 0) <= task.get("estimated_duration", 1) else 0
        retry_penalty = task.get("retry_count", 0) * 0.05
        return round(max(min(base + duration_bonus - retry_penalty + random.uniform(-0.05, 0.1), 1.0), 0), 2)

    def _count_errors(self, task: dict) -> float:
        if task.get("status") == "failed":
            return 1.0
        if task.get("error_message"):
            return 0.5
        return random.choice([0, 0, 0, 0.5])

    def _score_efficiency(self, task: dict) -> float:
        estimated = task.get("estimated_duration", 1)
        actual = task.get("actual_duration", estimated)
        if estimated == 0:
            return 0.5
        ratio = estimated / max(actual, 1)
        return round(min(ratio, 1.5) / 1.5, 2)

    def _score_satisfaction(self, quality: float, requirements: float) -> float:
        return round(min((quality + requirements) / 2 + random.uniform(-0.05, 0.05), 1.0), 2)


quality_evaluation = QualityEvaluation()
