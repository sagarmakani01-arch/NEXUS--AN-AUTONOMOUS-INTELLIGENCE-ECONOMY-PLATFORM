from __future__ import annotations

import logging
import random

from app.execution import persistence as ep

logger = logging.getLogger("nexus.execution.failure")

RECOVERY_STRATEGIES = {
    "retry": {"max_retries": 3, "backoff_factor": 1.5},
    "delegate": {"prefer_different_agent": True},
    "simplify": {"reduce_scope": 0.3},
    "abort": {"notify_stakeholders": True},
}


class FailureHandler:
    async def handle_task_failure(self, task_id: str, error: str, context: dict | None = None) -> dict:
        task = await ep.get_execution_task(task_id)
        if not task:
            return {"error": "Task not found"}

        retry_count = task.get("retry_count", 0)
        max_retries = task.get("max_retries", 3)
        failure_type = self._classify_failure(error, context)

        strategy = await self._select_strategy(task, failure_type, retry_count, max_retries)

        action_result = await self._execute_strategy(task_id, task, strategy, error)

        logger.info("failure_handled task=%s type=%s strategy=%s", task_id, failure_type, strategy["action"])
        return {
            "task_id": task_id,
            "failure_type": failure_type,
            "error": error,
            "strategy": strategy["action"],
            "action_result": action_result,
            "retry_count": retry_count,
        }

    async def handle_project_failure(self, project_id: str, failed_task_id: str, error: str) -> dict:
        project = await ep.get_project(project_id)
        if not project:
            return {"error": "Project not found"}

        failed_tasks = project.get("failed_tasks", 0) + 1
        await ep.update_project(project_id, failed_tasks=failed_tasks)

        if failed_tasks >= project.get("total_tasks", 0) * 0.5:
            await ep.update_project(project_id, status="on_hold")
            return {"project_id": project_id, "status": "on_hold", "reason": "Too many failures"}

        return {"project_id": project_id, "failed_tasks": failed_tasks, "action": "continue"}

    def _classify_failure(self, error: str, context: dict | None = None) -> str:
        error_lower = error.lower()
        if "timeout" in error_lower or "timed out" in error_lower:
            return "timeout"
        if "resource" in error_lower or "memory" in error_lower or "capacity" in error_lower:
            return "resource_exhaustion"
        if "permission" in error_lower or "access" in error_lower or "denied" in error_lower:
            return "permission_error"
        if "dependency" in error_lower or "unavailable" in error_lower:
            return "dependency_failure"
        if "invalid" in error_lower or "format" in error_lower or "parse" in error_lower:
            return "invalid_input"
        return "generic_error"

    async def _select_strategy(self, task: dict, failure_type: str, retry_count: int, max_retries: int) -> dict:
        if retry_count < max_retries and failure_type in ("timeout", "resource_exhaustion", "generic_error"):
            return {"action": "retry", "delay": retry_count * 2}
        if failure_type == "dependency_failure" and retry_count < 2:
            return {"action": "retry", "delay": 5}
        if retry_count >= max_retries and failure_type != "permission_error":
            return {"action": "delegate", "reason": "Max retries exceeded"}
        if failure_type == "permission_error":
            return {"action": "abort", "reason": "Permission denied"}
        if failure_type == "invalid_input":
            return {"action": "simplify", "reason": "Input validation failed"}
        return {"action": "abort", "reason": "Unrecoverable error"}

    async def _execute_strategy(self, task_id: str, task: dict, strategy: dict, error: str) -> dict:
        action = strategy["action"]
        if action == "retry":
            await ep.update_execution_task(
                task_id, status="created", retry_count=task.get("retry_count", 0) + 1,
                error_message=error,
            )
            return {"retried": True, "next_retry": task.get("retry_count", 0) + 1}
        elif action == "delegate":
            await ep.update_execution_task(
                task_id, agent_id=None, status="created",
                retry_count=0, error_message=f"Delegated after failure: {error}",
            )
            return {"delegated": True, "reason": strategy.get("reason", "")}
        elif action == "simplify":
            await ep.update_execution_task(
                task_id, status="created",
                description=task.get("description", "") + " [Simplified scope]",
                error_message=error,
            )
            return {"simplified": True}
        else:
            await ep.update_execution_task(
                task_id, status="failed", error_message=error,
            )
            return {"aborted": True, "reason": strategy.get("reason", "")}


failure_handler = FailureHandler()
