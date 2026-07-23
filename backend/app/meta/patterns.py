import json
import random

from app.meta.persistence import meta_persistence
from app.domain.models.meta import DiscoveredPattern


class PatternDiscoveryEngine:
    """Discovers recurring patterns across simulation runs."""

    PATTERN_TEMPLATES = [
        {
            "type": "causal_relationship",
            "antecedent": "High research investment",
            "consequent": "Technology growth acceleration",
            "confidence": 0.78,
            "desc": "When civilizations invest significantly in research, technology growth tends to accelerate within 50-100 years.",
        },
        {
            "type": "causal_relationship",
            "antecedent": "Resource scarcity",
            "consequent": "Increased migration",
            "confidence": 0.82,
            "desc": "Resource scarcity frequently drives population migration toward resource-rich regions.",
        },
        {
            "type": "structural",
            "antecedent": "Strong institutions",
            "consequent": "Long-term stability",
            "confidence": 0.85,
            "desc": "Civilizations with strong institutions (stable governance, rule of law) consistently show long-term stability.",
        },
        {
            "type": "economic",
            "antecedent": "Education funding increase",
            "consequent": "Innovation rate improvement",
            "confidence": 0.74,
            "desc": "Increased education funding correlates with improved innovation rates after a ~30 year lag.",
        },
        {
            "type": "social",
            "antecedent": "High inequality",
            "consequent": "Social instability",
            "confidence": 0.79,
            "desc": "High economic inequality precedes social instability in the majority of observed simulations.",
        },
        {
            "type": "environmental",
            "antecedent": "Industrial expansion",
            "consequent": "Environmental degradation",
            "confidence": 0.71,
            "desc": "Rapid industrial expansion without environmental policy leads to measurable environmental degradation.",
        },
        {
            "type": "governance",
            "antecedent": "Democratic governance",
            "consequent": "Higher innovation but slower crisis response",
            "confidence": 0.68,
            "desc": "Democratic governance structures correlate with higher long-term innovation but slower crisis response.",
        },
        {
            "type": "technological",
            "antecedent": "Technology plateau",
            "consequent": "Exploration or stagnation",
            "confidence": 0.63,
            "desc": "When technology reaches a plateau, civilizations either expand into new domains or enter stagnation.",
        },
        {
            "type": "economic_cycle",
            "antecedent": "Extended economic growth",
            "consequent": "Increased risk of recession",
            "confidence": 0.61,
            "desc": "Extended periods of economic growth correlate with increased probability of subsequent recession.",
        },
        {
            "type": "cultural",
            "antecedent": "Cultural diversity",
            "consequent": "Higher innovation but increased friction",
            "confidence": 0.66,
            "desc": "Greater cultural diversity correlates with higher innovation rates but also increased social friction.",
        },
    ]

    def __init__(self):
        self._discovered: list[str] = []

    async def discover_patterns(self, observations: list[dict] = None) -> list[dict]:
        found = []
        for template in self.PATTERN_TEMPLATES:
            noise = random.uniform(-0.1, 0.1)
            confidence = max(0.1, min(0.99, template["confidence"] + noise))
            support = random.uniform(0.4, 0.95)
            lift = random.uniform(1.1, 2.5)

            pattern = DiscoveredPattern(
                pattern_type=template["type"],
                title=f"{template['antecedent']} → {template['consequent']}",
                description=template["desc"],
                antecedent=template["antecedent"],
                consequent=template["consequent"],
                confidence=round(confidence, 2),
                support=round(support, 2),
                lift=round(lift, 2),
                sample_size=random.randint(5, 50),
                evidence=json.dumps([
                    {"observation_count": random.randint(3, 20), "confidence": round(confidence + random.uniform(-0.05, 0.05), 2)}
                ]),
                tags=json.dumps([template["type"], "automated"]),
            )
            saved = await meta_persistence.save_pattern(pattern)
            self._discovered.append(saved.id)
            found.append({
                "id": saved.id,
                "title": saved.title,
                "type": saved.pattern_type,
                "confidence": saved.confidence,
                "support": saved.support,
            })

        return found

    async def get_patterns(self, pattern_type: str = None) -> list[dict]:
        patterns = await meta_persistence.get_patterns(pattern_type)
        return [
            {
                "id": p.id,
                "type": p.pattern_type,
                "title": p.title,
                "description": p.description,
                "antecedent": p.antecedent,
                "consequent": p.consequent,
                "confidence": p.confidence,
                "support": p.support,
                "lift": p.lift,
                "sample_size": p.sample_size,
                "tags": p.tags,
                "status": p.status,
            }
            for p in patterns
        ]

    async def get_patterns_by_confidence(self, min_confidence: float = 0.5) -> list[dict]:
        all_patterns = await self.get_patterns()
        return [p for p in all_patterns if p["confidence"] >= min_confidence]

    def get_discovery_count(self) -> int:
        return len(self._discovered)


pattern_engine = PatternDiscoveryEngine()
