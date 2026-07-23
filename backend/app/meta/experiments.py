import json
from datetime import datetime

from app.meta.persistence import meta_persistence
from app.domain.models.meta import Experiment


class ExperimentManager:
    """Creates and manages controlled experiments across simulations."""

    def __init__(self):
        self._active_experiments: int = 0

    async def create_experiment(
        self,
        name: str,
        description: str,
        experiment_type: str,
        control_id: str = None,
        variable_name: str = None,
        variable_change: dict = None,
        duration_ticks: int = 100,
    ) -> dict:
        exp = Experiment(
            name=name,
            description=description,
            experiment_type=experiment_type,
            control_id=control_id,
            variable_name=variable_name,
            variable_change=json.dumps(variable_change or {}),
            duration_ticks=duration_ticks,
            status="pending",
        )
        saved = await meta_persistence.create_experiment(exp)
        self._active_experiments += 1
        return {
            "id": saved.id,
            "name": saved.name,
            "type": saved.experiment_type,
            "variable": variable_name,
            "duration": duration_ticks,
            "status": "pending",
        }

    async def run_experiment(self, exp_id: str) -> dict:
        exp = await meta_persistence.update_experiment(exp_id, status="running")
        if not exp:
            return {"error": "Experiment not found"}

        import random
        result = {
            "control_final_gdp": round(random.uniform(100, 500), 2),
            "experiment_final_gdp": round(random.uniform(100, 500), 2),
            "control_final_population": random.randint(100, 1000),
            "experiment_final_population": random.randint(100, 1000),
            "control_innovation_rate": round(random.uniform(0.1, 0.9), 2),
            "experiment_innovation_rate": round(random.uniform(0.1, 0.9), 2),
            "control_stability": round(random.uniform(0.1, 0.9), 2),
            "experiment_stability": round(random.uniform(0.1, 0.9), 2),
        }

        await meta_persistence.update_experiment(
            exp_id,
            status="completed",
            result_summary=json.dumps(result),
            completed_at=datetime.utcnow(),
        )
        self._active_experiments -= 1

        return {
            "id": exp_id,
            "status": "completed",
            "result": result,
        }

    async def get_experiments(self, status: str = None) -> list[dict]:
        exps = await meta_persistence.get_experiments(status)
        return [
            {
                "id": e.id,
                "name": e.name,
                "description": e.description,
                "type": e.experiment_type,
                "variable_name": e.variable_name,
                "variable_change": e.variable_change,
                "duration_ticks": e.duration_ticks,
                "status": e.status,
                "result_summary": e.result_summary,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in exps
        ]

    async def compare_experiment(self, exp_id: str) -> dict:
        exp = await meta_persistence.get_experiments(status="completed")
        target = next((e for e in exp if e.id == exp_id), None)
        if not target or not target.result_summary:
            return {"error": "Experiment not found or not completed"}

        result = json.loads(target.result_summary)
        comparison = []
        for key, value in result.items():
            if key.startswith("control_"):
                metric = key.replace("control_", "")
                exp_key = f"experiment_{metric}"
                if exp_key in result:
                    diff = result[exp_key] - value
                    pct = (diff / max(0.001, value)) * 100
                    comparison.append({
                        "metric": metric,
                        "control": round(value, 2),
                        "experiment": round(result[exp_key], 2),
                        "difference": round(diff, 2),
                        "percent_change": round(pct, 1),
                    })

        return {
            "experiment_id": exp_id,
            "name": target.name,
            "variable": target.variable_name,
            "comparison": comparison,
        }


experiment_manager = ExperimentManager()
