from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TriggerType(str, Enum):
    CONTRACT_OFFER = "contract_offer"
    COMPANY_INVITATION = "company_invitation"
    NEGOTIATION = "negotiation"
    PROMOTION = "promotion"
    INVESTMENT_OPPORTUNITY = "investment_opportunity"
    EMERGENCY = "emergency"
    SKILL_SELECTION = "skill_selection"
    COMPANY_CREATION = "company_creation"
    HIRING = "hiring"
    FIRING = "firing"
    GOAL_SELECTION = "goal_selection"
    TASK_ACCEPTANCE = "task_acceptance"
    MARKET_DECISION = "market_decision"
    RELATIONSHIP_DECISION = "relationship_decision"


TRIGGER_WEIGHTS: dict[TriggerType, int] = {
    TriggerType.CONTRACT_OFFER: 7,
    TriggerType.COMPANY_INVITATION: 6,
    TriggerType.NEGOTIATION: 8,
    TriggerType.PROMOTION: 6,
    TriggerType.INVESTMENT_OPPORTUNITY: 7,
    TriggerType.EMERGENCY: 10,
    TriggerType.SKILL_SELECTION: 4,
    TriggerType.COMPANY_CREATION: 8,
    TriggerType.HIRING: 7,
    TriggerType.FIRING: 9,
    TriggerType.GOAL_SELECTION: 5,
    TriggerType.TASK_ACCEPTANCE: 5,
    TriggerType.MARKET_DECISION: 6,
    TriggerType.RELATIONSHIP_DECISION: 5,
}


RELATED_TRIGGERS: dict[TriggerType, list[TriggerType]] = {
    TriggerType.CONTRACT_OFFER: [TriggerType.TASK_ACCEPTANCE, TriggerType.NEGOTIATION],
    TriggerType.COMPANY_INVITATION: [TriggerType.HIRING, TriggerType.COMPANY_CREATION],
    TriggerType.NEGOTIATION: [TriggerType.CONTRACT_OFFER, TriggerType.MARKET_DECISION],
    TriggerType.PROMOTION: [TriggerType.SKILL_SELECTION, TriggerType.GOAL_SELECTION],
    TriggerType.INVESTMENT_OPPORTUNITY: [TriggerType.MARKET_DECISION, TriggerType.NEGOTIATION],
    TriggerType.EMERGENCY: [TriggerType.RELATIONSHIP_DECISION, TriggerType.FIRING],
    TriggerType.SKILL_SELECTION: [TriggerType.PROMOTION, TriggerType.GOAL_SELECTION],
    TriggerType.COMPANY_CREATION: [TriggerType.HIRING, TriggerType.COMPANY_INVITATION],
    TriggerType.HIRING: [TriggerType.COMPANY_CREATION, TriggerType.COMPANY_INVITATION],
    TriggerType.FIRING: [TriggerType.HIRING, TriggerType.EMERGENCY],
    TriggerType.GOAL_SELECTION: [TriggerType.SKILL_SELECTION, TriggerType.PROMOTION],
    TriggerType.TASK_ACCEPTANCE: [TriggerType.CONTRACT_OFFER, TriggerType.MARKET_DECISION],
    TriggerType.MARKET_DECISION: [TriggerType.NEGOTIATION, TriggerType.INVESTMENT_OPPORTUNITY],
    TriggerType.RELATIONSHIP_DECISION: [TriggerType.EMERGENCY, TriggerType.COMPANY_INVITATION],
}


@dataclass
class DecisionTrigger:
    trigger_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_type: TriggerType = TriggerType.TASK_ACCEPTANCE
    agent_id: str = ""
    priority: int = 5
    context: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    expires_at: str | None = None
    requires_llm: bool = True

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > datetime.fromisoformat(self.expires_at)

    def to_dict(self) -> dict:
        return {
            "trigger_id": self.trigger_id,
            "trigger_type": self.trigger_type.value,
            "agent_id": self.agent_id,
            "priority": self.priority,
            "context": self.context,
            "timestamp": self.timestamp,
            "expires_at": self.expires_at,
            "requires_llm": self.requires_llm,
        }


def create_trigger(
    trigger_type: TriggerType,
    agent_id: str,
    context: dict | None = None,
    priority: int | None = None,
    expires_in_seconds: int | None = None,
    requires_llm: bool = True,
) -> DecisionTrigger:
    if priority is None:
        priority = TRIGGER_WEIGHTS.get(trigger_type, 5)

    expires_at = None
    if expires_in_seconds is not None:
        from datetime import timedelta

        expires_at = (
            datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        ).isoformat()

    return DecisionTrigger(
        trigger_type=trigger_type,
        agent_id=agent_id,
        priority=priority,
        context=context or {},
        expires_at=expires_at,
        requires_llm=requires_llm,
    )
