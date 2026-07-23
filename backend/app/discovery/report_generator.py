import json
import logging
import random

from app.discovery import persistence as db

logger = logging.getLogger("nexus.discovery.report")


async def generate_report(
    experiment_id: str | None = None,
    pattern_id: str | None = None,
    hypothesis_id: str | None = None,
    agent_id: str | None = None,
) -> dict:
    experiment = None
    pattern = None
    hypothesis = None

    if experiment_id:
        experiment = await db.get_experiment(experiment_id)
    if pattern_id:
        pattern = await db.get_pattern(pattern_id)
    if hypothesis_id:
        hypothesis = await db.get_hypothesis(hypothesis_id)

    title = _generate_title(experiment, pattern, hypothesis)
    research_question = _generate_research_question(experiment, pattern, hypothesis)
    methodology = _generate_methodology(experiment)
    simulation_setup = _generate_simulation_setup(experiment)
    results = _generate_results(experiment, pattern, hypothesis)
    limitations = _generate_limitations(experiment)
    future_experiments = _generate_future_experiments(experiment, pattern, hypothesis)

    confidence = _calculate_confidence(experiment, pattern, hypothesis)

    report = await db.create_report(
        title=title,
        research_question=research_question,
        methodology=methodology,
        simulation_setup=simulation_setup,
        results=results,
        limitations=limitations,
        future_experiments=future_experiments,
        confidence_score=confidence,
        status="published",
        created_by_agent_id=agent_id,
    )

    return report


def _generate_title(experiment: dict | None, pattern: dict | None, hypothesis: dict | None) -> str:
    if experiment:
        return f"Experiment Report: {experiment.get('title', 'Untitled')}"
    if pattern:
        return f"Pattern Analysis: {pattern.get('title', 'Untitled')}"
    if hypothesis:
        return f"Hypothesis Investigation: {hypothesis.get('title', 'Untitled')}"
    return "General Research Report"


def _generate_research_question(experiment: dict | None, pattern: dict | None, hypothesis: dict | None) -> str:
    if experiment:
        return experiment.get("research_question", "How do system variables interact?")
    if pattern:
        return f"What explains the observed {pattern.get('pattern_type', 'unknown')} pattern?"
    if hypothesis:
        return f"Can we validate the hypothesis: {hypothesis.get('description', '')[:100]}?"
    return "What are the fundamental dynamics of the simulated system?"


def _generate_methodology(experiment: dict | None) -> str:
    if experiment:
        variables = experiment.get("variables", {})
        return (
            f"A controlled experiment was designed with {len(variables)} variable(s): "
            f"{', '.join(variables.keys())}. "
            f"The experiment ran for {experiment.get('duration_ticks', 100)} simulation ticks. "
            "Control and test groups were compared using statistical analysis."
        )
    return "Multiple simulation runs were analyzed using correlation and trend analysis methods."


def _generate_simulation_setup(experiment: dict | None) -> str:
    if experiment:
        params = experiment.get("simulation_params", {})
        return (
            f"Simulation configured with parameters: {json.dumps(params, indent=2)}. "
            f"Laboratory type: {experiment.get('laboratory_type', 'general')}."
        )
    return "Standard simulation environment with default parameters."


def _generate_results(experiment: dict | None, pattern: dict | None, hypothesis: dict | None) -> str:
    parts = []
    if experiment:
        summary = experiment.get("result_summary")
        if summary:
            try:
                data = json.loads(summary) if isinstance(summary, str) else summary
                parts.append(f"Experiment achieved confidence score of {experiment.get('confidence_score', 0):.2f}.")
                if "effect_sizes" in data:
                    parts.append(f"Effect sizes: {json.dumps(data['effect_sizes'])}")
                if "significant" in data:
                    parts.append(f"Result {'is' if data['significant'] else 'is not'} statistically significant.")
            except (json.JSONDecodeError, TypeError):
                parts.append(f"Results summary: {summary[:200]}")
        else:
            parts.append("Experiment completed but no detailed results available.")
    if pattern:
        parts.append(
            f"Pattern discovered: {pattern.get('description', '')} "
            f"(confidence: {pattern.get('confidence', 0):.2f}, "
            f"support: {pattern.get('support', 0):.2f})"
        )
    if hypothesis:
        parts.append(
            f"Hypothesis confidence: {hypothesis.get('confidence_level', 0):.2f}. "
            f"Status: {hypothesis.get('status', 'unknown')}."
        )
    return "\n".join(parts) if parts else "No significant results were obtained."


def _generate_limitations(experiment: dict | None) -> str:
    limitations = [
        "Limited simulation duration may not capture long-term effects.",
        "Simplified variable interactions may omit confounding factors.",
        "Random seed variation introduces noise into measurements.",
        "Single simulation run limits generalizability of findings.",
    ]
    chosen = random.sample(limitations, min(2, len(limitations)))
    return "\n".join(chosen)


def _generate_future_experiments(experiment: dict | None, pattern: dict | None, hypothesis: dict | None) -> str:
    ideas = [
        "Extend simulation duration to capture long-term effects.",
        "Add additional control variables to isolate causal mechanisms.",
        "Run multiple iterations with different random seeds.",
        "Test interaction effects between multiple variables.",
        "Explore parameter space with broader value ranges.",
    ]
    chosen = random.sample(ideas, min(3, len(ideas)))
    return "\n".join(chosen)


def _calculate_confidence(experiment: dict | None, pattern: dict | None, hypothesis: dict | None) -> float:
    scores = []
    if experiment:
        scores.append(experiment.get("confidence_score", 0.0))
    if pattern:
        scores.append(pattern.get("confidence", 0.0))
    if hypothesis:
        scores.append(hypothesis.get("confidence_level", 0.0))
    return round(sum(scores) / len(scores), 4) if scores else 0.5
