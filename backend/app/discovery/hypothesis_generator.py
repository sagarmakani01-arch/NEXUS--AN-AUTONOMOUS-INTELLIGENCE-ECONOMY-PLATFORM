import json
import logging
import random

from app.discovery import persistence as db
from app.discovery.pattern_discovery import discover_patterns

logger = logging.getLogger("nexus.discovery.hypothesis")


DOMAIN_TEMPLATES = {
    "economy": [
        "Increased {antecedent} leads to higher {consequent} in growing economies",
        "High {antecedent} reduces {consequent} over extended periods",
        "Communities with balanced {antecedent} achieve optimal {consequent}",
    ],
    "social": [
        "Strong {antecedent} networks amplify {consequent} across generations",
        "Frequent {antecedent} correlates with improved {consequent} outcomes",
        "Diverse {antecedent} enriches long-term {consequent} potential",
    ],
    "technology": [
        "Accelerated {antecedent} creates exponential growth in {consequent}",
        "Investment in {antecedent} produces delayed but sustained {consequent} benefits",
        "Open {antecedent} systems outperform closed systems in {consequent}",
    ],
    "governance": [
        "Decentralized {antecedent} improves {consequent} due to local adaptation",
        "High {antecedent} participation increases {consequent} legitimacy",
        "Adaptive {antecedent} policies yield better {consequent} than static ones",
    ],
    "environment": [
        "Stable {antecedent} enables predictable {consequent} growth",
        "Resource-rich {antecedent} creates dependency that reduces {consequent} resilience",
        "Diverse {antecedent} buffers against {consequent} volatility",
    ],
    "general": [
        "The relationship between {antecedent} and {consequent} is mediated by unknown third variables",
        "{antecedent} acts as a catalyst for {consequent} under specific threshold conditions",
        "The effect of {antecedent} on {consequent} follows a U-shaped curve",
    ],
}


async def generate_hypothesis_from_pattern(pattern_id: str) -> dict | None:
    pattern = await db.get_pattern(pattern_id)
    if not pattern:
        return None

    antecedent = pattern.get("antecedent", "unknown_factor")
    consequent = pattern.get("consequent", "unknown_outcome")

    domain = _infer_domain(antecedent, consequent)
    templates = DOMAIN_TEMPLATES.get(domain, DOMAIN_TEMPLATES["general"])
    template = random.choice(templates)

    explanation = template.format(antecedent=antecedent.replace("_", " "), consequent=consequent.replace("_", " "))

    evidence = [{
        "source": "pattern_analysis",
        "pattern_id": pattern_id,
        "confidence": pattern.get("confidence", 0.5),
        "method": pattern.get("method", "unknown"),
    }]

    hypothesis = await db.create_hypothesis(
        title=f"Hypothesis: {antecedent} -> {consequent}",
        description=explanation,
        phenomenon=f"Observed {pattern.get('pattern_type', 'correlation')} between {antecedent} and {consequent}",
        proposed_explanation=explanation,
        supporting_evidence=json.dumps(evidence),
        counterexamples=json.dumps([]),
        confidence_level=pattern.get("confidence", 0.5) * random.uniform(0.7, 0.95),
        status="proposed",
        domain=domain,
        created_by="discovery_engine",
    )

    return hypothesis


async def generate_hypothesis_from_observation(observation: str, domain: str = "general") -> dict:
    templates = DOMAIN_TEMPLATES.get(domain, DOMAIN_TEMPLATES["general"])
    template = random.choice(templates)

    hypothesis = await db.create_hypothesis(
        title=f"Hypothesis from observation",
        description=template.format(antecedent="observed factor", consequent="system outcome"),
        phenomenon=observation,
        proposed_explanation=template.format(antecedent="the observed factor", consequent="system behavior"),
        supporting_evidence=json.dumps([]),
        counterexamples=json.dumps([]),
        confidence_level=random.uniform(0.1, 0.3),
        status="proposed",
        domain=domain,
        created_by="researcher",
    )

    return hypothesis


def _infer_domain(antecedent: str, consequent: str) -> str:
    domain_keywords = {
        "economy": ["economy", "trade", "market", "wealth", "investment", "funding", "tax", "price", "revenue"],
        "social": ["social", "community", "trust", "communication", "education", "culture", "population", "mobility"],
        "technology": ["technology", "innovation", "knowledge", "research", "tech", "science", "compute"],
        "governance": ["governance", "policy", "regulation", "law", "vote", "authority", "decentralization"],
        "environment": ["environment", "resource", "climate", "population", "density", "abundance"],
    }

    all_text = f"{antecedent} {consequent}".lower()
    scores = {}
    for dom, keywords in domain_keywords.items():
        scores[dom] = sum(1 for kw in keywords if kw in all_text)

    return max(scores, key=scores.get) if max(scores.values()) > 0 else "general"
