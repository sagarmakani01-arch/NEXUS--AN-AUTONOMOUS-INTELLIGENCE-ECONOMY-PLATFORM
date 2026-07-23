from app.meta.persistence import meta_persistence
from app.domain.models.meta import CrossSimulationResult


class CrossSimulationAnalyzer:
    """Compares outcomes across simulation runs."""

    async def compare(
        self,
        sim_a_id: str,
        sim_b_id: str,
        observations_a: list,
        observations_b: list,
        comparison_type: str = "metric",
    ) -> list[dict]:
        if not observations_a or not observations_b:
            return []

        latest_a = observations_a[0]
        latest_b = observations_b[0] if observations_b else observations_a[0]
        metrics = [
            ("population", "population", "Population"),
            ("economy_gdp", "economy_gdp", "GDP"),
            ("research_level", "research_level", "Research"),
            ("technology_level", "technology_level", "Technology"),
            ("education_index", "education_index", "Education"),
            ("governance_stability", "governance_stability", "Governance Stability"),
            ("environment_health", "environment_health", "Environment Health"),
            ("innovation_rate", "innovation_rate", "Innovation"),
            ("social_stability", "social_stability", "Social Stability"),
        ]

        results = []
        for attr_a, attr_b, name in metrics:
            val_a = getattr(latest_a, attr_a, 0) or 0
            val_b = getattr(latest_b, attr_b, 0) or 0
            diff = val_a - val_b
            pct = ((val_a - val_b) / max(0.001, val_b)) * 100

            result = CrossSimulationResult(
                simulation_a_id=sim_a_id,
                simulation_b_id=sim_b_id,
                comparison_type=comparison_type,
                metric=name,
                value_a=val_a,
                value_b=val_b,
                difference=diff,
                percent_change=pct,
                summary=f"{name}: {val_a:.1f} vs {val_b:.1f} ({pct:+.1f}%)",
            )
            saved = await meta_persistence.save_cross_result(result)
            results.append({
                "id": saved.id,
                "metric": name,
                "value_a": val_a,
                "value_b": val_b,
                "difference": round(diff, 2),
                "percent_change": round(pct, 1),
            })

        return results

    async def get_results(self) -> list[dict]:
        results = await meta_persistence.get_cross_results()
        return [
            {
                "id": r.id,
                "simulation_a": r.simulation_a_id,
                "simulation_b": r.simulation_b_id,
                "metric": r.metric,
                "value_a": r.value_a,
                "value_b": r.value_b,
                "difference": r.difference,
                "percent_change": r.percent_change,
                "summary": r.summary,
            }
            for r in results
        ]

    async def find_best_in_metric(self, metric: str) -> list[dict]:
        results = await meta_persistence.get_cross_results()
        metric_results = [r for r in results if r.metric.lower() == metric.lower()]
        metric_results.sort(key=lambda r: r.difference, reverse=True)
        return [
            {
                "sim_a": r.simulation_a_id,
                "sim_b": r.simulation_b_id,
                "difference": r.difference,
                "summary": r.summary,
            }
            for r in metric_results[:10]
        ]


analyzer = CrossSimulationAnalyzer()
