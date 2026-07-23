import json
import logging
import random

from app.research import persistence as db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.research.peer_review")

REVIEW_DECISIONS = ["accepted", "rejected", "revision_required"]
DECISION_WEIGHTS = {"accepted": 0.4, "revision_required": 0.35, "rejected": 0.25}


class PeerReviewEngine:
    def __init__(self):
        self.stats = {
            "reviews_submitted": 0,
            "accepted": 0,
            "rejected": 0,
            "revision_required": 0,
        }

    async def submit_review(self, publication_id: str, reviewer_agent_id: str,
                            institution: str | None = None,
                            decision: str | None = None) -> dict:
        if not decision:
            decision = self._determine_decision()

        methodology = random.uniform(0.3, 1.0)
        originality = random.uniform(0.3, 1.0)
        significance = random.uniform(0.3, 1.0)
        clarity = random.uniform(0.3, 1.0)
        overall = (methodology + originality + significance + clarity) / 4

        comments = self._generate_comments(decision, overall)
        suggestions = self._generate_suggestions(decision)

        review_id = await db.create_peer_review(
            publication_id=publication_id,
            reviewer_agent_id=reviewer_agent_id,
            institution=institution,
            decision=decision,
            methodology_score=round(methodology, 3),
            originality_score=round(originality, 3),
            significance_score=round(significance, 3),
            clarity_score=round(clarity, 3),
            overall_score=round(overall, 3),
            comments=comments,
            suggestions=json.dumps(suggestions),
            time_spent_hours=round(random.uniform(1, 8), 1),
        )
        self.stats["reviews_submitted"] += 1
        self.stats[decision.replace("_required", "").replace("ed", "ed" if decision == "accepted" else "ed")] = \
            self.stats.get(decision, 0) + 1

        if decision == "accepted":
            self.stats["accepted"] += 1
        elif decision == "rejected":
            self.stats["rejected"] += 1
        elif decision == "revision_required":
            self.stats["revision_required"] += 1

        pub = await db.get_publication(publication_id)
        if pub:
            review_status_map = {
                "accepted": "accepted", "rejected": "rejected",
                "revision_required": "revision_needed",
            }
            await db.update_publication(
                publication_id,
                peer_review_status=review_status_map.get(decision, "under_review"),
            )

        await dispatch(Event(EventType.PEER_REVIEW_COMPLETED, {
            "review_id": review_id, "publication_id": publication_id,
            "reviewer_agent_id": reviewer_agent_id, "decision": decision,
            "overall_score": round(overall, 3),
        }))

        return {
            "review_id": review_id, "decision": decision,
            "overall_score": round(overall, 3),
            "comments": comments,
        }

    async def get_reviews_for_publication(self, pub_id: str) -> list[dict]:
        return await db.list_peer_reviews(publication_id=pub_id)

    async def get_reviewer_stats(self, reviewer_id: str) -> dict:
        reviews = await db.list_peer_reviews(reviewer_agent_id=reviewer_id)
        return {
            "total_reviews": len(reviews),
            "average_score": round(
                sum(r["overall_score"] for r in reviews) / max(len(reviews), 1), 3
            ),
            "decisions": {
                d: len([r for r in reviews if r["decision"] == d])
                for d in REVIEW_DECISIONS
            },
        }

    def _determine_decision(self) -> str:
        r = random.random()
        cumulative = 0
        for decision, weight in DECISION_WEIGHTS.items():
            cumulative += weight
            if r <= cumulative:
                return decision
        return "accepted"

    def _generate_comments(self, decision: str, score: float) -> str:
        if decision == "accepted":
            return f"Strong paper with solid methodology (score: {score:.2f}). Recommend publication."
        elif decision == "rejected":
            return f"Insufficient rigor or novelty (score: {score:.2f}). Cannot recommend publication."
        else:
            return f"Promising work but needs revision (score: {score:.2f}). Address methodology concerns."

    def _generate_suggestions(self, decision: str) -> list[str]:
        suggestions = {
            "accepted": ["Consider expanding the discussion section"],
            "rejected": ["Fundamental methodology needs reassessment", "Insufficient novelty"],
            "revision_required": ["Strengthen experimental validation", "Add more baselines",
                                  "Clarify contribution claims", "Improve statistical analysis"],
        }
        return random.sample(suggestions.get(decision, []), k=min(2, len(suggestions.get(decision, []))))

    def get_state(self) -> dict:
        return {"stats": self.stats.copy()}


peer_review_engine = PeerReviewEngine()
