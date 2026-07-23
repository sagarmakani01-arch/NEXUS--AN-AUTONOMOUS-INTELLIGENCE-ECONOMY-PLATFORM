from __future__ import annotations

import logging
import random

from app.marketplace import persistence as mp

logger = logging.getLogger("nexus.marketplace.negotiation")

CONCESSION_PATTERNS = [
    {"type": "meet_halfway", "factor": 0.5},
    {"type": "small_concession", "factor": 0.2},
    {"type": "generous_concession", "factor": 0.8},
    {"type": "hold_firm", "factor": 0.0},
]


class NegotiationEngine:
    async def negotiate(
        self, proposal_id: str, agent_id: str, agent_personality: dict | None = None,
    ) -> dict:
        proposal = await mp.get_proposal(proposal_id)
        if not proposal or proposal["status"] != "countered":
            return {"error": "No active counter to negotiate"}

        counter_reward = proposal.get("counter_reward", 0)
        original = proposal.get("proposed_reward", 0)

        if agent_personality:
            agreeableness = agent_personality.get("agreeableness", 0.5)
            neuroticism = agent_personality.get("neuroticism", 0.5)
        else:
            agreeableness = random.uniform(0.3, 0.8)
            neuroticism = random.uniform(0.1, 0.6)

        if agreeableness > 0.7:
            pattern = random.choice(CONCESSION_PATTERNS[:3])
        elif neuroticism > 0.6:
            pattern = random.choice([CONCESSION_PATTERNS[0], CONCESSION_PATTERNS[3]])
        else:
            pattern = random.choice(CONCESSION_PATTERNS)

        midpoint = (original + counter_reward) / 2
        concession_amount = abs(counter_reward - original) * pattern["factor"]
        if counter_reward > original:
            new_offer = original + concession_amount
        else:
            new_offer = original - concession_amount

        new_offer = round(new_offer, 2)

        if pattern["type"] == "hold_firm":
            new_offer = original

        await mp.update_proposal(
            proposal_id, counter_reward=new_offer,
            counter_message=f"Negotiation: {pattern['type']} offer",
        )

        logger.info(
            "negotiation_round proposal=%s pattern=%s new_offer=%.0f",
            proposal_id, pattern["type"], new_offer,
        )
        return {
            "proposal_id": proposal_id,
            "new_offer": new_offer,
            "pattern": pattern["type"],
            "original": original,
            "counter": counter_reward,
        }

    async def resolve_negotiation(
        self, proposal_id: str, accept: bool = True,
    ) -> dict:
        proposal = await mp.get_proposal(proposal_id)
        if not proposal:
            return {"error": "Proposal not found"}

        if accept:
            final_reward = proposal.get("counter_reward") or proposal["proposed_reward"]
            await mp.update_proposal(
                proposal_id, status="accepted",
                proposed_reward=final_reward,
                counter_reward=None, counter_message=None,
            )
            await mp.update_task(proposal["task_id"], status="in_progress")
            logger.info("negotiation_resolved proposal=%s accepted reward=%.0f", proposal_id, final_reward)
            return {"status": "accepted", "final_reward": final_reward}
        else:
            await mp.update_proposal(proposal_id, status="rejected")
            logger.info("negotiation_resolved proposal=%s rejected", proposal_id)
            return {"status": "rejected"}


negotiation_engine = NegotiationEngine()
