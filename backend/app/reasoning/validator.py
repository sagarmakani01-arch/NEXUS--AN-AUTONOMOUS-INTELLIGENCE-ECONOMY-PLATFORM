from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("nexus.reasoning.validator")

REQUIRED_FIELDS = [
    "decision",
    "reasoning_summary",
    "confidence",
    "expected_outcome",
    "risk_level",
    "estimated_cost",
    "estimated_reward",
    "next_goal",
    "alternative_options",
]

SAFETY_RULES = [
    {"name": "budget_limit", "description": "Cost cannot exceed wallet balance + 10% overdraft"},
    {"name": "energy_check", "description": "Cannot work if energy is below 10%"},
    {"name": "confidence_minimum", "description": "Confidence must be at least 0.1"},
    {"name": "no_negative_cost", "description": "Cost cannot be negative"},
    {"name": "risk_consistency", "description": "High risk decisions must have confidence < 0.8"},
]

SIMULATION_RULES = [
    {"name": "resting_restriction", "description": "Agent cannot take actions while resting"},
    {"name": "dead_agent", "description": "Agent with 0 energy must rest first"},
]

ECONOMIC_RULES = [
    {"name": "affordability", "description": "Cost must not exceed available balance"},
    {"name": "reasonable_reward", "description": "Reward should be between 0 and 10000 NXC"},
    {"name": "cost_floor", "description": "Cost should be >= 0"},
]


class DecisionValidator:
    def validate(self, decision: dict, context: dict, trigger_type: str) -> tuple[bool, list[str], dict]:
        errors = []
        corrected = dict(decision)

        schema_errors = self.validate_schema(decision)
        errors.extend(schema_errors)

        safety_errors = self.validate_safety(decision, context)
        errors.extend(safety_errors)

        sim_errors = self.validate_simulation_rules(decision, context)
        errors.extend(sim_errors)

        econ_errors = self.validate_economic_rules(decision, context)
        errors.extend(econ_errors)

        conf_errors = self.validate_confidence(decision)
        errors.extend(conf_errors)

        risk_errors = self.validate_risk_level(decision)
        errors.extend(risk_errors)

        if errors:
            corrected = self.auto_correct(decision, errors, context)

        is_valid = len([e for e in errors if e.startswith("CRITICAL")]) == 0
        return is_valid, errors, corrected

    def validate_schema(self, decision: dict) -> list[str]:
        errors = []
        for field in REQUIRED_FIELDS:
            if field not in decision:
                errors.append(f"CRITICAL: Missing required field '{field}'")

        if "confidence" in decision:
            if not isinstance(decision["confidence"], (int, float)):
                errors.append("CRITICAL: 'confidence' must be a number")
            elif not (0 <= decision["confidence"] <= 1):
                errors.append(f"WARNING: confidence {decision['confidence']} out of range 0-1")

        if "estimated_cost" in decision:
            if not isinstance(decision["estimated_cost"], (int, float)):
                errors.append("CRITICAL: 'estimated_cost' must be a number")

        if "estimated_reward" in decision:
            if not isinstance(decision["estimated_reward"], (int, float)):
                errors.append("CRITICAL: 'estimated_reward' must be a number")

        if "alternative_options" in decision:
            if not isinstance(decision["alternative_options"], list):
                errors.append("WARNING: 'alternative_options' should be a list")

        return errors

    def validate_safety(self, decision: dict, context: dict) -> list[str]:
        errors = []
        agent = context.get("agent", {})
        wallet = agent.get("wallet_balance", 0)
        energy = agent.get("energy", 50)

        cost = decision.get("estimated_cost", 0)
        if cost > wallet * 1.1:
            errors.append(f"WARNING: Cost {cost:.0f} exceeds budget {wallet:.0f} (10% overdraft limit)")

        if energy < 10 and decision.get("decision", "").lower() in ("work", "accept", "start_project"):
            errors.append("WARNING: Agent energy is very low, working is risky")

        confidence = decision.get("confidence", 0.5)
        if confidence < 0.1:
            errors.append("WARNING: Very low confidence decision")

        if cost < 0:
            errors.append("WARNING: Negative cost is unusual")

        risk = decision.get("risk_level", "medium")
        if risk == "high" and confidence > 0.8:
            errors.append("WARNING: High-risk decision with high confidence seems inconsistent")

        return errors

    def validate_simulation_rules(self, decision: dict, context: dict) -> list[str]:
        errors = []
        agent = context.get("agent", {})
        status = agent.get("current_status", "idle")

        if status == "resting":
            action = decision.get("decision", "").lower()
            if action not in ("rest", "wait", "recover"):
                errors.append("WARNING: Agent is resting but decision is not rest-related")

        energy = agent.get("energy", 50)
        if energy <= 0:
            errors.append("WARNING: Agent has no energy, must rest")

        return errors

    def validate_economic_rules(self, decision: dict, context: dict) -> list[str]:
        errors = []
        agent = context.get("agent", {})
        wallet = agent.get("wallet_balance", 0)

        cost = decision.get("estimated_cost", 0)
        if cost < 0:
            errors.append("WARNING: Negative cost")

        reward = decision.get("estimated_reward", 0)
        if reward < 0:
            errors.append("WARNING: Negative reward")
        if reward > 10000:
            errors.append("WARNING: Very high estimated reward, seems unrealistic")

        if cost > 0 and reward == 0:
            action = decision.get("decision", "").lower()
            if "invest" in action or "purchase" in action or "buy" in action:
                errors.append("INFO: Spending with no expected reward")

        return errors

    def validate_confidence(self, decision: dict) -> list[str]:
        errors = []
        confidence = decision.get("confidence", None)
        if confidence is None:
            errors.append("WARNING: No confidence level set")
        elif not isinstance(confidence, (int, float)):
            errors.append("CRITICAL: Confidence must be a number")
        elif not (0 <= confidence <= 1):
            errors.append(f"WARNING: Confidence {confidence} outside valid range 0-1")
        return errors

    def validate_risk_level(self, decision: dict) -> list[str]:
        errors = []
        risk = decision.get("risk_level", None)
        if risk is None:
            errors.append("WARNING: No risk level set")
        elif risk not in ("low", "medium", "high"):
            errors.append(f"CRITICAL: Invalid risk_level '{risk}', must be low/medium/high")
        return errors

    def auto_correct(self, decision: dict, errors: list[str], context: dict) -> dict:
        corrected = dict(decision)

        if "confidence" in corrected:
            corrected["confidence"] = max(0.0, min(1.0, float(corrected["confidence"])))

        if corrected.get("risk_level") not in ("low", "medium", "high"):
            corrected["risk_level"] = "medium"

        agent = context.get("agent", {})
        wallet = agent.get("wallet_balance", 0)
        if corrected.get("estimated_cost", 0) > wallet * 1.1:
            corrected["estimated_cost"] = round(wallet * 0.9, 2)

        if corrected.get("estimated_cost", 0) < 0:
            corrected["estimated_cost"] = 0.0

        if corrected.get("estimated_reward", 0) < 0:
            corrected["estimated_reward"] = 0.0

        if "alternative_options" not in corrected or not isinstance(corrected.get("alternative_options"), list):
            corrected["alternative_options"] = ["Continue current path"]

        if "reasoning_summary" not in corrected:
            corrected["reasoning_summary"] = "Decision made based on available context."

        return corrected
