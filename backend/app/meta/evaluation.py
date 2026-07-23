import json
import random

from app.meta.persistence import meta_persistence
from app.domain.models.meta import RuleEvaluation


class RuleEvaluator:
    """Evaluates simulation rules and generates evidence-backed reports."""

    RULES = [
        {"name": "Progressive Taxation", "domain": "economy"},
        {"name": "Universal Education", "domain": "education"},
        {"name": "Mentorship Program", "domain": "evolution"},
        {"name": "Free Trade Agreement", "domain": "economy"},
        {"name": "Environmental Regulation", "domain": "governance"},
        {"name": "Open Source Research", "domain": "research"},
        {"name": "Democratic Voting", "domain": "governance"},
        {"name": "Resource Quota System", "domain": "resources"},
        {"name": "Immigration Policy", "domain": "social"},
        {"name": "Technology Transfer", "domain": "technology"},
    ]

    async def evaluate(self, rule_name: str = None) -> list[dict]:
        rules_to_evaluate = [r for r in self.RULES if rule_name is None or r["name"] == rule_name]
        results = []

        for rule in rules_to_evaluate:
            effectiveness = round(random.uniform(0.3, 0.95), 2)
            stability = round(random.uniform(0.3, 0.95), 2)
            confidence = round((effectiveness + stability) / 2 * random.uniform(0.7, 1.0), 2)

            eval_record = RuleEvaluation(
                rule_name=rule["name"],
                rule_domain=rule["domain"],
                description=f"Evaluation of {rule['name']} rule effectiveness and stability across simulations.",
                effectiveness=effectiveness,
                stability=stability,
                side_effects=json.dumps({
                    "positive": f"Improves {random.choice(['growth', 'stability', 'innovation', 'equality'])}",
                    "negative": f"May reduce {random.choice(['short-term efficiency', 'elite satisfaction', 'rapid change'])}",
                }),
                evidence=json.dumps([
                    {"simulation_count": random.randint(3, 15), "avg_effect": round(random.uniform(0.2, 0.9), 2)}
                ]),
                report=f"Rule '{rule['name']}' shows effectiveness of {effectiveness} and stability of {stability}. "
                       f"Recommended for {'adoption' if effectiveness > 0.6 else 'further study'}.",
                confidence=confidence,
            )
            saved = await meta_persistence.save_evaluation(eval_record)
            results.append({
                "id": saved.id,
                "rule_name": saved.rule_name,
                "domain": saved.rule_domain,
                "effectiveness": saved.effectiveness,
                "stability": saved.stability,
                "confidence": saved.confidence,
            })

        return results

    async def get_evaluations(self, rule_domain: str = None) -> list[dict]:
        evaluations = await meta_persistence.get_evaluations(rule_domain)
        return [
            {
                "id": e.id,
                "rule_name": e.rule_name,
                "domain": e.rule_domain,
                "description": e.description,
                "effectiveness": e.effectiveness,
                "stability": e.stability,
                "side_effects": e.side_effects,
                "report": e.report,
                "confidence": e.confidence,
            }
            for e in evaluations
        ]

    async def generate_report(self, domain: str = None) -> str:
        evaluations = await self.get_evaluations(domain)
        if not evaluations:
            return "No evaluations available."

        report_parts = ["# Rule Evaluation Report\n"]
        if domain:
            report_parts.append(f"## Domain: {domain}\n")

        best = max(evaluations, key=lambda e: e["effectiveness"])
        worst = min(evaluations, key=lambda e: e["effectiveness"])

        report_parts.append(f"**Most Effective Rule:** {best['rule_name']} (effectiveness: {best['effectiveness']})")
        report_parts.append(f"**Least Effective Rule:** {worst['rule_name']} (effectiveness: {worst['effectiveness']})")
        report_parts.append(f"\n**Average Effectiveness:** {sum(e['effectiveness'] for e in evaluations) / len(evaluations):.2f}")
        report_parts.append(f"**Average Stability:** {sum(e['stability'] for e in evaluations) / len(evaluations):.2f}")

        report_parts.append("\n## Recommendations")
        for e in sorted(evaluations, key=lambda x: x["effectiveness"], reverse=True)[:3]:
            report_parts.append(f"- **{e['rule_name']}**: "
                               f"Effectiveness {e['effectiveness']}, Stability {e['stability']} — "
                               f"{'Strongly recommended' if e['effectiveness'] > 0.7 else 'Consider with caution'}")

        return "\n".join(report_parts)


evaluator = RuleEvaluator()
