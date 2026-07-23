from app.meta.persistence import meta_persistence


class ExplainabilityEngine:
    """Provides transparent explanations for recommendations and findings."""

    async def explain_recommendation(self, rec_id: str) -> dict:
        recs = await meta_persistence.get_recommendations()
        rec = next((r for r in recs if r.id == rec_id), None)
        if not rec:
            return {"error": "Recommendation not found"}

        evidence_data = rec.evidence or "[]"
        evidence_list = json.loads(evidence_data) if isinstance(evidence_data, str) else evidence_data

        simulations_data = rec.supporting_simulations or "[]"
        sim_list = json.loads(simulations_data) if isinstance(simulations_data, str) else simulations_data

        return {
            "recommendation": rec.title,
            "evidence": [
                {
                    "source": e.get("source", "Unknown"),
                    "studies": e.get("studies", 0),
                    "observed_improvement": e.get("avg_improvement", "N/A"),
                }
                for e in evidence_list
            ],
            "supporting_simulations": sim_list,
            "confidence": rec.confidence,
            "limitations": rec.limitations or "No limitations specified.",
            "summary": f"Recommendation '{rec.title}' is based on analysis across "
                       f"{len(sim_list)} simulations with an average confidence of {rec.confidence:.0%}. "
                       f"The expected impact is: {rec.expected_impact or 'N/A'}.",
        }

    async def explain_pattern(self, pattern_id: str) -> dict:
        patterns = await meta_persistence.get_patterns()
        pattern = next((p for p in patterns if p.id == pattern_id), None)
        if not pattern:
            return {"error": "Pattern not found"}

        return {
            "pattern": pattern.title,
            "description": pattern.description,
            "antecedent": pattern.antecedent,
            "consequent": pattern.consequent,
            "evidence_level": f"Confidence: {pattern.confidence:.0%}, "
                              f"Support: {pattern.support:.0%}, "
                              f"Lift: {pattern.lift:.2f}",
            "sample_size": pattern.sample_size,
            "methodology": f"This pattern was discovered by analyzing {pattern.sample_size} simulation runs "
                           f"looking for correlations between '{pattern.antecedent}' and '{pattern.consequent}'.",
        }

    async def explain_experiment_result(self, exp_id: str) -> dict:
        from app.meta.experiments import experiment_manager
        result = await experiment_manager.compare_experiment(exp_id)
        if "error" in result:
            return result

        variable = result.get("variable", "unknown")
        comparison = result.get("comparison", [])

        explanation_parts = [
            f"## Experiment: {result.get('name', 'Unknown')}",
            f"\n**Variable Changed:** {variable}",
            f"\n**Results:**",
        ]

        for comp in comparison:
            direction = "improved" if comp["experiment"] > comp["control"] else "declined"
            explanation_parts.append(
                f"- {comp['metric']}: {direction} by {abs(comp['percent_change']):.1f}% "
                f"({comp['experiment']} vs {comp['control']})"
            )

        return {
            "experiment_id": exp_id,
            "name": result.get("name"),
            "variable": variable,
            "comparison": comparison,
            "explanation": "\n".join(explanation_parts),
        }


import json

explainer = ExplainabilityEngine()
