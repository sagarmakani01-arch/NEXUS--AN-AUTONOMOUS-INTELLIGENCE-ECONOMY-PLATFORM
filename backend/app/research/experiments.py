import json
import logging
import random
from datetime import datetime, timezone

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.experiments")

OUTCOME_WEIGHTS = {
    "success": 0.3,
    "partial_success": 0.35,
    "failure": 0.2,
    "unexpected_result": 0.15,
}


class ExperimentEngine:
    def __init__(self):
        self.stats = {
            "experiments_run": 0,
            "successful": 0,
            "failed": 0,
            "unexpected": 0,
            "total_compute": 0,
            "total_budget": 0,
        }

    async def create_experiment(self, project_id: str, title: str,
                                description: str | None = None,
                                methodology: str | None = None,
                                hypothesis: str | None = None,
                                variables: dict | None = None) -> dict:
        exp_id = await db.create_experiment(
            project_id=project_id, title=title,
            description=description, methodology=methodology,
            hypothesis=hypothesis, variables=json.dumps(variables or {}),
        )
        return {"experiment_id": exp_id, "title": title, "status": "planned"}

    async def start_experiment(self, experiment_id: str) -> dict:
        exp = await db.get_experiment(experiment_id)
        if not exp:
            return {"success": False, "error": "Experiment not found"}
        if exp["status"] not in ("planned",):
            return {"success": False, "error": f"Cannot start experiment in status: {exp['status']}"}

        now = datetime.now(timezone.utc).isoformat()
        await db.update_experiment(experiment_id, status="running", started_at=now)
        return {"success": True, "experiment_id": experiment_id, "status": "running"}

    async def complete_experiment(self, experiment_id: str,
                                  force_outcome: str | None = None) -> dict:
        exp = await db.get_experiment(experiment_id)
        if not exp:
            return {"success": False, "error": "Experiment not found"}

        outcome = force_outcome or self._determine_outcome()
        time_spent = random.uniform(1, 10)
        budget_consumed = random.uniform(5, 30)
        compute_consumed = random.uniform(10, 100)
        confidence = random.uniform(0.3, 0.9)

        knowledge_produced = []
        unexpected = []
        if outcome in ("success", "partial_success"):
            num_knowledge = random.randint(1, 3)
            for _ in range(num_knowledge):
                knowledge_produced.append({
                    "name": f"Discovery from {exp.get('title', 'Experiment')}",
                    "type": random.choice(["concept", "method", "discovery"]),
                    "confidence": round(confidence, 2),
                })
        if outcome == "unexpected_result":
            unexpected.append({
                "finding": f"Unexpected observation in {exp.get('title', 'Experiment')}",
                "significance": random.uniform(0.5, 1.0),
            })

        now = datetime.now(timezone.utc).isoformat()
        await db.update_experiment(
            experiment_id, status="completed", outcome=outcome,
            outcome_details=f"Experiment completed with outcome: {outcome}",
            confidence_score=round(confidence, 3),
            time_spent=round(time_spent, 1),
            budget_consumed=round(budget_consumed, 2),
            compute_consumed=round(compute_consumed, 1),
            knowledge_produced=json.dumps(knowledge_produced),
            unexpected_findings=json.dumps(unexpected),
            completed_at=now,
        )

        self.stats["experiments_run"] += 1
        self.stats["total_compute"] += compute_consumed
        self.stats["total_budget"] += budget_consumed
        if outcome == "success":
            self.stats["successful"] += 1
        elif outcome == "failure":
            self.stats["failed"] += 1
        elif outcome == "unexpected_result":
            self.stats["unexpected"] += 1

        project = await db.get_project(exp["project_id"])
        if project:
            progress_gain = {"success": 20, "partial_success": 10, "failure": 3, "unexpected_result": 8}
            new_progress = min(100, project["progress"] + progress_gain.get(outcome, 5))
            await db.update_project(exp["project_id"], progress=round(new_progress, 1))

        await dispatch(Event(EventType.EXPERIMENT_COMPLETED, {
            "experiment_id": experiment_id, "project_id": exp["project_id"],
            "outcome": outcome, "knowledge_produced": len(knowledge_produced),
        }))

        return {
            "success": True, "experiment_id": experiment_id,
            "outcome": outcome, "confidence": round(confidence, 3),
            "knowledge_produced": len(knowledge_produced),
            "unexpected_findings": len(unexpected),
        }

    def _determine_outcome(self) -> str:
        r = random.random()
        cumulative = 0
        for outcome, weight in OUTCOME_WEIGHTS.items():
            cumulative += weight
            if r <= cumulative:
                return outcome
        return "partial_success"

    async def get_experiment(self, experiment_id: str) -> dict | None:
        return await db.get_experiment(experiment_id)

    async def list_experiments(self, project_id: str | None = None,
                               status: str | None = None) -> list[dict]:
        return await db.list_experiments(project_id, status)

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


experiment_engine = ExperimentEngine()
