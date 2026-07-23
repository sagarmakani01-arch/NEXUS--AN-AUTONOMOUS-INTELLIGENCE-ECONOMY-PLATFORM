import json
import random
import time
from typing import Any, Dict, Optional

from .base import BaseProvider


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _pick(options: list, seed: Optional[str] = None) -> str:
    if seed:
        idx = hash(seed) % len(options)
        return options[idx]
    return random.choice(options)


class DeterministicProvider(BaseProvider):
    """Rule-based provider that operates without any external API keys."""

    def __init__(self) -> None:
        self._model = "deterministic-v1"

    # ------------------------------------------------------------------
    # BaseProvider interface
    # ------------------------------------------------------------------

    @property
    def provider_name(self) -> str:
        return "deterministic"

    @property
    def is_available(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> dict:
        start = time.monotonic()

        context = self._parse_context(prompt)
        trigger = context["trigger"]
        personality = context["personality"]
        goals = context["goals"]
        wallet = context["wallet"]

        decision = self._decide(
            trigger=trigger,
            personality=personality,
            goals=goals,
            wallet=wallet,
            raw_prompt=prompt,
        )

        decision_text = json.dumps(decision, ensure_ascii=False)
        latency_ms = (time.monotonic() - start) * 1000

        return {
            "text": decision_text,
            "tokens_used": len(prompt.split()) + len(decision_text.split()),
            "model": self._model,
            "latency_ms": round(latency_ms, 2),
        }

    async def health_check(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # Prompt parsing
    # ------------------------------------------------------------------

    def _parse_context(self, prompt: str) -> dict:
        prompt_lower = prompt.lower()

        trigger = "unknown"
        for t in [
            "contract_offer",
            "company_invitation",
            "negotiation",
            "skill_selection",
            "investment_opportunity",
            "emergency",
            "hiring",
            "promotion",
            "company_creation",
            "goal_selection",
        ]:
            if t.replace("_", " ") in prompt_lower or t in prompt_lower:
                trigger = t
                break

        if trigger == "unknown":
            if "contract" in prompt_lower and ("offer" in prompt_lower or "propos" in prompt_lower):
                trigger = "contract_offer"
            elif "invit" in prompt_lower or "join" in prompt_lower:
                trigger = "company_invitation"
            elif "negoti" in prompt_lower or "counter" in prompt_lower:
                trigger = "negotiation"
            elif "skill" in prompt_lower or "learn" in prompt_lower or "train" in prompt_lower:
                trigger = "skill_selection"
            elif "invest" in prompt_lower or "fund" in prompt_lower:
                trigger = "investment_opportunity"
            elif "emergenc" in prompt_lower or "urgent" in prompt_lower or "critical" in prompt_lower:
                trigger = "emergency"
            elif "hire" in prompt_lower or "recruit" in prompt_lower:
                trigger = "hiring"
            elif "promot" in prompt_lower or "advance" in prompt_lower:
                trigger = "promotion"
            elif "creat" in prompt_lower and "compan" in prompt_lower:
                trigger = "company_creation"
            elif "goal" in prompt_lower or "objective" in prompt_lower:
                trigger = "goal_selection"

        personality = self._extract_personality(prompt)
        goals = self._extract_list(prompt, "goals")
        wallet = self._extract_number(prompt, "wallet") or self._extract_number(prompt, "balance")

        return {
            "trigger": trigger,
            "personality": personality,
            "goals": goals,
            "wallet": wallet,
        }

    def _extract_personality(self, prompt: str) -> dict:
        defaults = {
            "risk_tolerance": 0.5,
            "conscientiousness": 0.5,
            "agreeableness": 0.5,
            "extraversion": 0.5,
            "openness": 0.5,
            "neuroticism": 0.3,
            "cooperation": 0.5,
            "leadership": 0.5,
            "ambition": 0.5,
            "curiosity": 0.5,
            "reliability": 0.5,
            "learning_speed": 0.5,
        }
        for trait in defaults:
            val = self._extract_number(prompt, trait)
            if val is not None:
                defaults[trait] = _clamp(val)
        return defaults

    def _extract_list(self, prompt: str, key: str) -> list:
        idx = prompt.lower().find(key)
        if idx == -1:
            return []
        snippet = prompt[idx : idx + 500]
        start = snippet.find("[")
        end = snippet.find("]")
        if start != -1 and end > start:
            try:
                return json.loads(snippet[start : end + 1])
            except json.JSONDecodeError:
                return [s.strip().strip('"').strip("'") for s in snippet[start + 1 : end].split(",")]
        return []

    def _extract_number(self, prompt: str, key: str) -> Optional[float]:
        import re

        pattern = rf"{key}\s*[:=]\s*([0-9]*\.?[0-9]+)"
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return float(match.group(1))
        return None

    # ------------------------------------------------------------------
    # Decision logic per trigger type
    # ------------------------------------------------------------------

    def _decide(
        self,
        trigger: str,
        personality: dict,
        goals: list,
        wallet: Optional[float],
        raw_prompt: str,
    ) -> dict:
        handler = getattr(self, f"_handle_{trigger}", self._handle_unknown)
        return handler(personality, goals, wallet, raw_prompt)

    def _base_response(
        self,
        action: str,
        confidence: float,
        reasoning: str,
        alternatives: list,
        extra: Optional[dict] = None,
    ) -> dict:
        resp: dict[str, Any] = {
            "decision": action,
            "confidence": round(_clamp(confidence), 2),
            "reasoning": reasoning,
            "alternatives": alternatives,
            "provider": self.provider_name,
        }
        if extra:
            resp.update(extra)
        return resp

    # -- 1. contract_offer --------------------------------------------------

    def _handle_contract_offer(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        risk = p["risk_tolerance"]
        conscience = p["conscientiousness"]
        reward_factor = self._extract_number(raw, "reward") or self._extract_number(raw, "payment") or 5000
        cost_factor = self._extract_number(raw, "cost") or self._extract_number(raw, "penalty") or 2000

        value_score = reward_factor / max(cost_factor, 1)
        risk_score = 1.0 - risk

        if value_score > 2.0 and risk_score > 0.3:
            action = "accept"
            confidence = _clamp(0.6 + value_score * 0.1 + risk * 0.2)
            reasoning = (
                f"Contract offers favourable value (reward/cost={value_score:.1f}). "
                f"Risk tolerance ({risk:.0%}) supports acceptance. "
                f"Conscientiousness ({conscience:.0%}) indicates ability to deliver."
            )
        elif value_score < 0.8 or risk_score < 0.2:
            action = "decline"
            confidence = _clamp(0.5 + (1 - value_score) * 0.2 + risk_score * 0.15)
            reasoning = (
                f"Contract value ratio ({value_score:.1f}) is unattractive or risk profile "
                f"exceeds tolerance. Declining to protect resources."
            )
        else:
            action = "negotiate"
            confidence = _clamp(0.4 + abs(0.5 - value_score) * 0.3)
            reasoning = (
                f"Contract has moderate value ({value_score:.1f}). "
                f"Attempting to negotiate better terms."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["accept", "decline", "negotiate", "request_more_info"],
            extra={"value_ratio": round(value_score, 2), "estimated_reward": reward_factor, "estimated_cost": cost_factor},
        )

    # -- 2. company_invitation ----------------------------------------------

    def _handle_company_invitation(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        coop = p["cooperation"]
        lead = p["leadership"]
        extraversion = p["extraversion"]

        social_score = (coop + extraversion) / 2
        independence = 1.0 - lead * 0.5

        if coop > 0.7 and social_score > 0.6:
            action = "accept"
            confidence = _clamp(0.55 + coop * 0.3)
            reasoning = (
                f"High cooperation ({coop:.0%}) and social orientation ({social_score:.0%}) "
                f"make joining a company attractive. Team environment aligns with personality."
            )
        elif lead > 0.7 and independence > 0.5:
            action = "decline_and_start_own"
            confidence = _clamp(0.5 + lead * 0.3)
            reasoning = (
                f"Strong leadership ({lead:.0%}) suggests ability to lead rather than follow. "
                f"Starting own company may yield better outcomes."
            )
        else:
            action = "request_more_info"
            confidence = _clamp(0.4 + social_score * 0.2)
            reasoning = (
                f"Moderate social orientation ({social_score:.0%}). "
                f"Gathering more information before committing."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["accept", "decline", "decline_and_start_own", "request_more_info", "negotiate_terms"],
            extra={"social_orientation": round(social_score, 2)},
        )

    # -- 3. negotiation -----------------------------------------------------

    def _handle_negotiation(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        agree = p["agreeableness"]
        risk = p["risk_tolerance"]
        extraversion = p["extraversion"]

        if agree > 0.7 and risk < 0.4:
            action = "accept_terms"
            confidence = _clamp(0.55 + agree * 0.25)
            reasoning = (
                f"High agreeableness ({agree:.0%}) favours reaching agreement. "
                f"Low risk tolerance ({risk:.0%}) discourages prolonged negotiation."
            )
        elif risk > 0.6 and agree < 0.5:
            action = "push_harder"
            confidence = _clamp(0.5 + risk * 0.25)
            reasoning = (
                f"Risk tolerance ({risk:.0%}) supports aggressive negotiation. "
                f"Lower agreeableness ({agree:.0%}) enables harder stance."
            )
        else:
            action = "find_middle_ground"
            confidence = _clamp(0.45 + abs(agree - 0.5) * 0.2)
            reasoning = (
                f"Balanced personality profile suggests compromise approach. "
                f"Aim for mutually beneficial terms."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["accept_terms", "push_harder", "find_middle_ground", "walk_away", "delay"],
            extra={"agreeableness": round(agree, 2), "risk_tolerance": round(risk, 2)},
        )

    # -- 4. skill_selection -------------------------------------------------

    def _handle_skill_selection(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        curiosity = p["curiosity"]
        learn_speed = p["learning_speed"]
        openness = p["openness"]

        growth_score = (curiosity + openness + learn_speed) / 3

        high_value_skills = ["leadership", "negotiation", "engineering", "strategy", "management"]
        prompt_lower = raw.lower()
        detected_skill = _pick(high_value_skills, seed=prompt_lower)

        if curiosity > 0.7 or openness > 0.7:
            action = "learn_new_skill"
            confidence = _clamp(0.55 + growth_score * 0.3)
            reasoning = (
                f"High curiosity ({curiosity:.0%}) and openness ({openness:.0%}) indicate "
                f"strong appetite for learning. Investing in skill development yields long-term returns."
            )
        elif learn_speed < 0.3:
            action = "hire_specialist"
            confidence = _clamp(0.5 + (1 - learn_speed) * 0.25)
            reasoning = (
                f"Learning speed ({learn_speed:.0%}) is low. "
                f"Hiring or contracting a specialist is more efficient."
            )
        else:
            action = "incremental_improvement"
            confidence = _clamp(0.45 + growth_score * 0.2)
            reasoning = (
                f"Moderate growth profile ({growth_score:.0%}). "
                f"Focus on incremental skill improvements aligned with current goals."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["learn_new_skill", "hire_specialist", "incremental_improvement", "outsource", "skip"],
            extra={"growth_score": round(growth_score, 2), "suggested_skill": detected_skill},
        )

    # -- 5. investment_opportunity ------------------------------------------

    def _handle_investment_opportunity(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        risk = p["risk_tolerance"]
        conscience = p["conscientiousness"]
        current_wallet = wallet if wallet is not None else 10000

        potential_investment = self._extract_number(raw, "amount") or self._extract_number(raw, "investment") or 1000
        ratio = potential_investment / max(current_wallet, 1)

        if risk > 0.6 and ratio < 0.3 and conscience > 0.4:
            action = "invest"
            confidence = _clamp(0.5 + risk * 0.2 + (1 - ratio) * 0.15)
            reasoning = (
                f"Risk tolerance ({risk:.0%}) supports investment. "
                f"Investment ({potential_investment:,.0f}) is {ratio:.0%} of wallet ({current_wallet:,.0f}), "
                f"within safe bounds. Conscientiousness ({conscience:.0%}) ensures due diligence."
            )
        elif ratio > 0.5:
            action = "decline"
            confidence = _clamp(0.55 + ratio * 0.2)
            reasoning = (
                f"Investment ({potential_investment:,.0f}) represents {ratio:.0%} of wallet "
                f"({current_wallet:,.0f}). Too large relative to available resources."
            )
        else:
            action = "invest_fractional"
            safe_amount = current_wallet * min(0.15, risk * 0.2)
            confidence = _clamp(0.4 + risk * 0.15)
            reasoning = (
                f"Moderate risk profile. Investing a fractional amount ({safe_amount:,.0f}) "
                f"to limit exposure while participating."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["invest", "invest_fractional", "decline", "negotiate_lower_amount", "delay"],
            extra={
                "wallet_balance": current_wallet,
                "proposed_investment": potential_investment,
                "ratio": round(ratio, 3),
            },
        )

    # -- 6. emergency -------------------------------------------------------

    def _handle_emergency(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        conscience = p["conscientiousness"]
        reliability = p["reliability"]
        neuroticism = p["neuroticism"]

        readiness = (conscience + reliability) / 2
        stress_impact = neuroticism * 0.3

        if readiness > 0.6 and stress_impact < 0.3:
            action = "respond_immediately"
            confidence = _clamp(0.6 + readiness * 0.25 - stress_impact)
            reasoning = (
                f"High readiness score ({readiness:.0%}) indicates capacity to handle emergency. "
                f"Low stress impact ({stress_impact:.0%}) supports clear-headed response."
            )
        elif stress_impact > 0.4:
            action = "delegate"
            confidence = _clamp(0.5 + stress_impact * 0.2)
            reasoning = (
                f"Neuroticism ({neuroticism:.0%}) elevates stress during emergencies. "
                f"Delegating to a more composed party reduces risk of error."
            )
        else:
            action = "assess_then_act"
            confidence = _clamp(0.45 + readiness * 0.2)
            reasoning = (
                f"Moderate readiness ({readiness:.0%}). Taking time to assess before acting "
                f"to avoid missteps."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["respond_immediately", "delegate", "assess_then_act", "call_for_backup", "triage"],
            extra={"readiness": round(readiness, 2), "stress_impact": round(stress_impact, 2)},
        )

    # -- 7. hiring ----------------------------------------------------------

    def _handle_hiring(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        lead = p["leadership"]
        coop = p["cooperation"]
        ambition = p["ambition"]

        team_builder = (lead + coop) / 2

        if lead > 0.7 and coop > 0.5:
            action = "hire_complementary"
            confidence = _clamp(0.55 + team_builder * 0.25)
            reasoning = (
                f"Strong leadership ({lead:.0%}) and cooperation ({coop:.0%}) indicate ability "
                f"to build and lead a complementary team."
            )
        elif coop < 0.3:
            action = "hire_for_strength"
            confidence = _clamp(0.5 + (1 - coop) * 0.2)
            reasoning = (
                f"Lower cooperation ({coop:.0%}) suggests hiring individuals who strengthen "
                f"team dynamics and fill social gaps."
            )
        else:
            action = "hire_skill_gap"
            confidence = _clamp(0.45 + team_builder * 0.2)
            reasoning = (
                f"Balanced team-building profile. Focus hiring on identified skill gaps "
                f"rather than personality fit."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["hire_complementary", "hire_for_strength", "hire_skill_gap", "outsource", "delay_hiring"],
            extra={"team_builder_score": round(team_builder, 2)},
        )

    # -- 8. promotion -------------------------------------------------------

    def _handle_promotion(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        ambition = p["ambition"]
        lead = p["leadership"]
        conscience = p["conscientiousness"]

        readiness = (ambition + lead + conscience) / 3

        if ambition > 0.7 and lead > 0.6:
            action = "accept"
            confidence = _clamp(0.6 + readiness * 0.25)
            reasoning = (
                f"High ambition ({ambition:.0%}) and leadership ({lead:.0%}) indicate readiness "
                f"for increased responsibility. Promotion aligns with growth trajectory."
            )
        elif conscience < 0.4:
            action = "defer"
            confidence = _clamp(0.5 + (1 - conscience) * 0.2)
            reasoning = (
                f"Lower conscientiousness ({conscience:.0%}) suggests current role mastery "
                f"may be insufficient. Building foundation before advancing."
            )
        else:
            action = "accept_with_conditions"
            confidence = _clamp(0.5 + readiness * 0.15)
            reasoning = (
                f"Moderate readiness ({readiness:.0%}). Accepting with negotiated conditions "
                f"for support, training, or timeline."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["accept", "accept_with_conditions", "defer", "negotiate_benefits", "decline"],
            extra={"readiness_score": round(readiness, 2)},
        )

    # -- 9. company_creation ------------------------------------------------

    def _handle_company_creation(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        lead = p["leadership"]
        risk = p["risk_tolerance"]
        ambition = p["ambition"]
        current_wallet = wallet if wallet is not None else 10000

        founder_score = (lead + risk + ambition) / 3
        min_safe_wallet = 5000

        if founder_score > 0.65 and current_wallet > min_safe_wallet:
            action = "proceed"
            confidence = _clamp(0.55 + founder_score * 0.25 - (1 - min(current_wallet / 20000, 1)) * 0.1)
            reasoning = (
                f"Founder score ({founder_score:.0%}) is strong. Leadership ({lead:.0%}), "
                f"risk tolerance ({risk:.0%}), and ambition ({ambition:.0%}) support entrepreneurship. "
                f"Wallet ({current_wallet:,.0f}) provides runway."
            )
        elif risk < 0.3:
            action = "validate_first"
            confidence = _clamp(0.5 + (1 - risk) * 0.2)
            reasoning = (
                f"Low risk tolerance ({risk:.0%}). Validating the idea with a minimal "
                f"pilot before full commitment reduces exposure."
            )
        else:
            action = "seek_cofounder"
            confidence = _clamp(0.45 + founder_score * 0.15)
            reasoning = (
                f"Moderate founder profile ({founder_score:.0%}). "
                f"Finding a complementary co-founder fills gaps and shares risk."
            )

        return self._base_response(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            alternatives=["proceed", "validate_first", "seek_cofounder", "delay", "research_market"],
            extra={"founder_score": round(founder_score, 2), "wallet_balance": current_wallet},
        )

    # -- 10. goal_selection -------------------------------------------------

    def _handle_goal_selection(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        ambition = p["ambition"]
        curiosity = p["curiosity"]
        conscientiousness = p["conscientiousness"]
        openness = p["openness"]

        if ambition > 0.7:
            recommended = "maximize_status_and_income"
            reasoning = (
                f"High ambition ({ambition:.0%}) drives toward status and income maximization. "
                f"Prioritizing high-reward objectives."
            )
        elif curiosity > 0.7 or openness > 0.7:
            recommended = "explore_and_learn"
            reasoning = (
                f"High curiosity ({curiosity:.0%}) and openness ({openness:.0%}) indicate "
                f"exploration and learning goals will be most fulfilling."
            )
        elif conscientiousness > 0.7:
            recommended = "build_stable_foundation"
            reasoning = (
                f"High conscientiousness ({conscientiousness:.0%}) favours building stable, "
                f"reliable foundations before pursuing high-risk objectives."
            )
        else:
            recommended = "balanced_growth"
            reasoning = (
                f"Balanced personality profile suggests a mixed strategy across "
                f"exploration, stability, and achievement."
            )

        available_goals = goals if goals else ["wealth", "knowledge", "relationships", "health", "impact"]

        return self._base_response(
            action=recommended,
            confidence=_clamp(0.5 + max(ambition, curiosity, conscientiousness) * 0.25),
            reasoning=reasoning,
            alternatives=["maximize_status_and_income", "explore_and_learn", "build_stable_foundation", "balanced_growth"],
            extra={"available_goals": available_goals, "personality_snapshot": {k: round(v, 2) for k, v in p.items()}},
        )

    # -- fallback -----------------------------------------------------------

    def _handle_unknown(self, p: dict, goals: list, wallet: Optional[float], raw: str) -> dict:
        return self._base_response(
            action="gather_more_context",
            confidence=0.3,
            reasoning="Unable to determine trigger type from prompt. Requesting additional context.",
            alternatives=["gather_more_context", "default_to_safest_option", "escalate"],
        )
