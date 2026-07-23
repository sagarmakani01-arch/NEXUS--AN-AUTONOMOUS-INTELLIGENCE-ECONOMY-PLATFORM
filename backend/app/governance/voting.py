import json
import logging
from datetime import datetime, timezone, timedelta

from app.governance import persistence as gov_db
from app.core.event_bus import Event, EventType, dispatch

logger = logging.getLogger("nexus.governance.voting")

PROPOSAL_TYPES = ["law", "policy", "budget", "personnel", "regulation"]
WEIGHT_FACTORS = ["equal", "reputation", "ownership", "participation"]


class VotingSystem:
    def __init__(self):
        self.stats = {
            "votes_started": 0,
            "votes_cast": 0,
            "votes_resolved": 0,
        }

    async def start_vote(self, proposal_title: str, description: str | None,
                         proposer_id: str, proposal_type: str = "law",
                         target_id: str | None = None,
                         options: list[str] | None = None,
                         total_eligible: int = 0, quorum_pct: float = 30.0,
                         weight_factor: str = "equal") -> dict:
        if proposal_type not in PROPOSAL_TYPES:
            proposal_type = "law"
        if weight_factor not in WEIGHT_FACTORS:
            weight_factor = "equal"

        vote_id = await gov_db.create_vote(
            proposal_title=proposal_title, description=description,
            proposer_id=proposer_id, proposal_type=proposal_type,
            target_id=target_id, options=options,
            total_eligible=total_eligible, quorum_pct=quorum_pct,
            weight_factor=weight_factor,
        )
        self.stats["votes_started"] += 1

        await gov_db.record_governance(
            record_type="vote_started", title=f"Vote: {proposal_title}",
            actor_id=proposer_id, description=description,
            related_ids=[vote_id],
            impact={"proposal_type": proposal_type, "quorum_pct": quorum_pct},
        )

        await dispatch(Event(EventType.VOTE_COMPLETED, {
            "vote_id": vote_id, "proposal_title": proposal_title,
            "proposer_id": proposer_id, "status": "started",
        }))

        return {
            "vote_id": vote_id,
            "proposal_title": proposal_title,
            "options": options or ["yes", "no"],
            "total_eligible": total_eligible,
            "quorum_pct": quorum_pct,
            "status": "open",
        }

    async def cast_vote(self, vote_id: str, voter_id: str, option: str) -> dict:
        vote = await gov_db.get_vote(vote_id)
        if not vote:
            return {"success": False, "error": "Vote not found"}
        if vote["status"] != "open":
            return {"success": False, "error": "Vote not open"}

        voters = vote.get("voters", {})
        if voter_id in voters:
            return {"success": False, "error": "Already voted"}

        options = vote.get("options", ["yes", "no"])
        if option not in options:
            return {"success": False, "error": "Invalid option"}

        voters[voter_id] = option
        tally = vote.get("tally", {})
        tally[option] = tally.get(option, 0) + 1

        await gov_db.update_vote(vote_id, voters=json.dumps(voters), tally=json.dumps(tally))
        self.stats["votes_cast"] += 1

        return {
            "success": True, "voter_id": voter_id,
            "option": option, "current_tally": tally,
        }

    async def resolve_vote(self, vote_id: str) -> dict:
        vote = await gov_db.get_vote(vote_id)
        if not vote:
            return {"success": False, "error": "Vote not found"}
        if vote["status"] != "open":
            return {"success": False, "error": "Vote already resolved"}

        tally = vote.get("tally", {})
        voters = vote.get("voters", {})
        total_eligible = vote.get("total_eligible", len(voters))
        quorum_pct = vote.get("quorum_pct", 30.0)

        turnout_pct = (len(voters) / total_eligible * 100) if total_eligible > 0 else 0

        if turnout_pct < quorum_pct:
            result = "failed_quorum"
            await gov_db.update_vote(
                vote_id, status="failed", result=f"Quorum not met ({turnout_pct:.1f}% < {quorum_pct}%)",
                resolved_at=datetime.now(timezone.utc),
            )
        else:
            max_option = max(tally, key=tally.get) if tally else None
            max_votes = tally.get(max_option, 0) if max_option else 0
            total_votes = sum(tally.values())

            if total_votes > 0 and max_votes / total_votes > 0.5:
                result = f"Approved: {max_option} ({max_votes}/{total_votes} votes)"
                await gov_db.update_vote(
                    vote_id, status="passed", result=result,
                    resolved_at=datetime.now(timezone.utc),
                )
            else:
                result = f"No clear majority: {tally}"
                await gov_db.update_vote(
                    vote_id, status="failed", result=result,
                    resolved_at=datetime.now(timezone.utc),
                )

        self.stats["votes_resolved"] += 1

        await dispatch(Event(EventType.VOTE_COMPLETED, {
            "vote_id": vote_id, "result": result,
            "tally": tally, "turnout_pct": turnout_pct,
        }))

        return {
            "vote_id": vote_id, "result": result,
            "tally": tally, "turnout_pct": round(turnout_pct, 2),
        }

    async def get_vote(self, vote_id: str) -> dict | None:
        return await gov_db.get_vote(vote_id)

    async def list_votes(self, status: str | None = None) -> list[dict]:
        return await gov_db.list_votes(status)

    def get_state(self) -> dict:
        return {
            "stats": self.stats.copy(),
            "proposal_types": PROPOSAL_TYPES,
            "weight_factors": WEIGHT_FACTORS,
        }


voting_system = VotingSystem()
