from __future__ import annotations

import logging
import random

from app.marketplace import persistence as mp

logger = logging.getLogger("nexus.marketplace.bidding")


class BiddingEngine:
    async def submit_proposal(
        self, task_id: str, agent_id: str, proposed_reward: float,
        cover_letter: str = "", estimated_duration: str = "",
    ) -> dict:
        existing = await mp.list_proposals_for_task(task_id)
        if any(p["agent_id"] == agent_id and p["status"] == "pending" for p in existing):
            logger.warning("duplicate_proposal task=%s agent=%s", task_id, agent_id)
            return {"error": "Already have a pending proposal for this task"}

        proposal = await mp.create_proposal(
            task_id=task_id, agent_id=agent_id, proposed_reward=proposed_reward,
            cover_letter=cover_letter, estimated_duration=estimated_duration,
        )
        logger.info("proposal_submitted task=%s agent=%s reward=%.0f", task_id, agent_id, proposed_reward)
        return proposal

    async def accept_proposal(self, proposal_id: str) -> dict:
        proposal = await mp.get_proposal(proposal_id)
        if not proposal or proposal["status"] != "pending":
            return {"error": "Proposal not found or not pending"}

        updated = await mp.update_proposal(proposal_id, status="accepted")
        await mp.update_task(proposal["task_id"], status="in_progress")

        other_proposals = await mp.list_proposals_for_task(proposal["task_id"])
        for p in other_proposals:
            if p["id"] != proposal_id and p["status"] == "pending":
                await mp.update_proposal(p["id"], status="rejected")

        logger.info("proposal_accepted proposal=%s task=%s", proposal_id, proposal["task_id"])
        return updated

    async def reject_proposal(self, proposal_id: str) -> dict:
        proposal = await mp.get_proposal(proposal_id)
        if not proposal or proposal["status"] != "pending":
            return {"error": "Proposal not found or not pending"}
        updated = await mp.update_proposal(proposal_id, status="rejected")
        logger.info("proposal_rejected proposal=%s", proposal_id)
        return updated

    async def counter_proposal(self, proposal_id: str, counter_reward: float, message: str = "") -> dict:
        proposal = await mp.get_proposal(proposal_id)
        if not proposal or proposal["status"] != "pending":
            return {"error": "Proposal not found or not pending"}
        updated = await mp.update_proposal(
            proposal_id, status="countered",
            counter_reward=counter_reward, counter_message=message,
        )
        logger.info("proposal_countered proposal=%s new_reward=%.0f", proposal_id, counter_reward)
        return updated

    async def accept_counter(self, proposal_id: str) -> dict:
        proposal = await mp.get_proposal(proposal_id)
        if not proposal or proposal["status"] != "countered":
            return {"error": "Proposal not found or not countered"}
        final_reward = proposal.get("counter_reward") or proposal["proposed_reward"]
        updated = await mp.update_proposal(
            proposal_id, status="accepted",
            proposed_reward=final_reward, counter_reward=None, counter_message=None,
        )
        await mp.update_task(proposal["task_id"], status="in_progress")
        logger.info("counter_accepted proposal=%s final_reward=%.0f", proposal_id, final_reward)
        return updated

    async def auto_bid(self, agent_id: str, agent_skills: list[str], agent_reputation: float = 50) -> list[dict]:
        tasks = await mp.list_tasks(status="open")
        bid_results = []
        for task in tasks[:3]:
            task_skills = task.get("required_skills", [])
            overlap = len(set(agent_skills) & set(task_skills))
            if overlap == 0 and random.random() > 0.3:
                continue
            base = task.get("reward", 50)
            adjustment = random.uniform(0.8, 1.2)
            proposed = round(base * adjustment, 2)
            duration_hours = random.randint(2, 48)
            result = await self.submit_proposal(
                task_id=task["id"], agent_id=agent_id,
                proposed_reward=proposed,
                cover_letter=f"Auto-bid: {overlap} skill matches, reputation {agent_reputation:.1f}",
                estimated_duration=f"{duration_hours}h",
            )
            if "error" not in result:
                bid_results.append(result)
        return bid_results

    async def get_task_bids(self, task_id: str) -> list[dict]:
        return await mp.list_proposals_for_task(task_id)

    async def get_agent_bids(self, agent_id: str, status: str = "") -> list[dict]:
        return await mp.list_proposals_by_agent(agent_id, status=status)


bidding_engine = BiddingEngine()
