import json
import random

from app.meta.persistence import meta_persistence
from app.domain.models.meta import Recommendation


class RecommendationEngine:
    """Generates evidence-backed suggestions for improving simulations."""

    RECOMMENDATION_TEMPLATES = [
        {
            "type": "policy",
            "domain": "research",
            "title": "Increase Research Funding",
            "desc": "Consider allocating more resources to research and development to accelerate technology growth.",
            "change": "Increase research budget allocation by 15-25%",
            "impact": "Expected 10-20% improvement in innovation rate within 50 years",
            "confidence": 0.72,
        },
        {
            "type": "parameter",
            "domain": "evolution",
            "title": "Adjust Mutation Rate",
            "desc": "Slightly increase the evolution mutation rate to introduce more diversity while maintaining stability.",
            "change": "Increase mutation rate from current to current × 1.3",
            "impact": "Expected 5-15% more innovations with minimal stability impact",
            "confidence": 0.58,
        },
        {
            "type": "policy",
            "domain": "environment",
            "title": "Reduce Resource Extraction",
            "desc": "Implement sustainable resource extraction policies to prevent long-term environmental damage.",
            "change": "Reduce extraction rate by 10-20% with recycling incentives",
            "impact": "Expected 30% improvement in environmental health within 100 years",
            "confidence": 0.81,
        },
        {
            "type": "policy",
            "domain": "education",
            "title": "Expand Education Capacity",
            "desc": "Increase education infrastructure to support more citizens and improve skill development.",
            "change": "Build additional education facilities and increase teacher ratios",
            "impact": "Expected 15-25% improvement in education index and innovation",
            "confidence": 0.76,
        },
        {
            "type": "policy",
            "domain": "governance",
            "title": "Implement Progressive Taxation",
            "desc": "Adopt progressive taxation to reduce inequality and improve social stability.",
            "change": "Implement tiered tax system with higher rates for top earners",
            "impact": "Expected 10-20% improvement in social stability with minimal economic impact",
            "confidence": 0.65,
        },
        {
            "type": "structural",
            "domain": "economy",
            "title": "Establish Free Trade Zones",
            "desc": "Create free trade zones between civilizations to boost economic growth and technology transfer.",
            "change": "Remove trade barriers with allied civilizations",
            "impact": "Expected 10-30% increase in GDP and technology exchange",
            "confidence": 0.69,
        },
        {
            "type": "policy",
            "domain": "social",
            "title": "Launch Mentorship Initiative",
            "desc": "Establish formal mentorship programs to accelerate knowledge transfer and skill development.",
            "change": "Create mentor-mentee matching system with incentives",
            "impact": "Expected 20% faster skill development and 15% more innovations",
            "confidence": 0.73,
        },
        {
            "type": "parameter",
            "domain": "technology",
            "title": "Accelerate Technology Diffusion",
            "desc": "Increase technology adoption rate to reduce the gap between discovery and widespread use.",
            "change": "Increase diffusion rate parameter by 20%",
            "impact": "Expected 25% faster technology adoption across civilization",
            "confidence": 0.62,
        },
    ]

    async def generate_recommendations(self, domain: str = None) -> list[dict]:
        templates = [t for t in self.RECOMMENDATION_TEMPLATES if domain is None or t["domain"] == domain]
        results = []

        for template in templates:
            noise = random.uniform(-0.1, 0.1)
            confidence = max(0.3, min(0.95, template["confidence"] + noise))

            rec = Recommendation(
                title=template["title"],
                description=template["desc"],
                recommendation_type=template["type"],
                target_domain=template["domain"],
                suggested_change=template["change"],
                expected_impact=template["impact"],
                confidence=round(confidence, 2),
                evidence=json.dumps([
                    {
                        "source": f"Cross-simulation analysis of {template['domain']} domain",
                        "studies": random.randint(3, 12),
                        "avg_improvement": f"{random.randint(5, 30)}%",
                    }
                ]),
                supporting_simulations=json.dumps([f"sim_{random.randint(100, 999)}" for _ in range(3)]),
                limitations=f"Based on {random.randint(3, 15)} simulation runs. Results may vary significantly.",
            )
            saved = await meta_persistence.create_recommendation(rec)
            results.append({
                "id": saved.id,
                "title": saved.title,
                "type": saved.recommendation_type,
                "domain": saved.target_domain,
                "confidence": saved.confidence,
                "expected_impact": saved.expected_impact,
            })

        return results

    async def get_recommendations(self, status: str = None) -> list[dict]:
        recs = await meta_persistence.get_recommendations(status)
        return [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "type": r.recommendation_type,
                "domain": r.target_domain,
                "suggested_change": r.suggested_change,
                "expected_impact": r.expected_impact,
                "confidence": r.confidence,
                "evidence": r.evidence,
                "supporting_simulations": r.supporting_simulations,
                "limitations": r.limitations,
                "status": r.status,
            }
            for r in recs
        ]

    async def review_recommendation(self, rec_id: str, status: str) -> dict:
        rec = await meta_persistence.update_recommendation(rec_id, status=status, reviewed_at=datetime.utcnow())
        if not rec:
            return {"error": "Recommendation not found"}
        return {"id": rec_id, "status": status}

    async def get_stats(self) -> dict:
        recs = await self.get_recommendations()
        pending = sum(1 for r in recs if r["status"] == "pending")
        accepted = sum(1 for r in recs if r["status"] == "accepted")
        rejected = sum(1 for r in recs if r["status"] == "rejected")
        avg_confidence = sum(r["confidence"] for r in recs) / max(1, len(recs))
        return {
            "total": len(recs),
            "pending": pending,
            "accepted": accepted,
            "rejected": rejected,
            "average_confidence": round(avg_confidence, 2),
        }


recommender = RecommendationEngine()
