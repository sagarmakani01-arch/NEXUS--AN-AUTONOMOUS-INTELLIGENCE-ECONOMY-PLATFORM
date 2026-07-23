from __future__ import annotations

import json
import logging
import random
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("nexus.reasoning.prompts")

OUTPUT_SCHEMA = {
    "decision": "str - the chosen action",
    "reasoning_summary": "str - brief explanation (1-2 sentences)",
    "confidence": "float 0.0-1.0",
    "expected_outcome": "str - what you expect to happen",
    "risk_level": "low|medium|high",
    "estimated_cost": "float - estimated cost in NXC",
    "estimated_reward": "float - estimated reward in NXC",
    "next_goal": "str - what to pursue after this decision",
    "alternative_options": "list[str] - other options considered",
}

DEFAULT_TEMPLATE = {
    "system": (
        "You are {display_name}, a {profession} in a digital economy simulation. "
        "You have {energy}% energy, {wallet_balance:.0f} NXC in your wallet, "
        "and a reputation of {reputation:.2f}. Make decisions that align with "
        "your personality and current goals. Always respond in valid JSON."
    ),
    "identity": "Agent: {display_name} | Profession: {profession} | Generation: {generation}",
    "personality": "Personality: {personality_traits}",
    "situation": "Current Situation: {situation}",
    "memories": "Relevant Past Experiences:\n{memories_list}",
    "goal": "Current Goal: {goal_title} ({goal_progress}/{goal_target})",
    "options": "Available Options:\n{options_list}",
    "constraints": "Constraints:\n{constraints_list}",
    "output_format": "Respond with ONLY a JSON object matching this schema:\n{schema}",
}


class PromptBuilder:
    def __init__(self, template_override: dict | None = None) -> None:
        self._template = {**DEFAULT_TEMPLATE, **(template_override or {})}

    def build(self, context: dict, trigger_type: str, options: list[dict] | None = None) -> str:
        agent = context.get("agent", {})
        identity = context.get("identity", {})
        personality = context.get("personality", {})
        goal = context.get("goal", {})
        memories = context.get("memories", [])
        constraints_raw = context.get("constraints", {})
        time_info = context.get("simulation_time", {})

        display_name = identity.get("display_name", agent.get("name", "Unknown"))
        profession = identity.get("profession", agent.get("profession", "Unknown"))
        generation = identity.get("generation", 1)
        energy = agent.get("energy", 50)
        wallet_balance = agent.get("wallet_balance", 0)
        reputation = agent.get("reputation", 0)

        personality_str = self._format_personality(personality)
        memories_str = self._format_memories(memories)
        constraints_str = self._format_constraints(constraints_raw or {
            "budget": wallet_balance,
            "energy": energy,
            "reputation": reputation,
        })

        situation = self._build_situation(context, trigger_type)
        goal_title = goal.get("title", "No active goal")
        goal_progress = goal.get("progress", 0)
        goal_target = goal.get("target", 1)

        system_msg = self._template["system"].format(
            display_name=display_name,
            profession=profession,
            energy=energy,
            wallet_balance=wallet_balance,
            reputation=reputation,
        )

        sections = [
            system_msg,
            "",
            self._template["identity"].format(
                display_name=display_name,
                profession=profession,
                generation=generation,
            ),
            self._template["personality"].format(personality_traits=personality_str),
            self._template["situation"].format(situation=situation),
            self._template["memories"].format(memories_list=memories_str),
            self._template["goal"].format(
                goal_title=goal_title,
                goal_progress=goal_progress,
                goal_target=goal_target,
            ),
        ]

        if options:
            options_list = "\n".join(
                f"  {i+1}. {opt.get('title', opt.get('name', str(opt)))}"
                for i, opt in enumerate(options)
            )
            sections.append(self._template["options"].format(options_list=options_list))

        sections.append(self._template["constraints"].format(constraints_list=constraints_str))
        sections.append(self._template["output_format"].format(
            schema=json.dumps(OUTPUT_SCHEMA, indent=2)
        ))

        return "\n\n".join(sections)

    def _build_situation(self, context: dict, trigger_type: str) -> str:
        parts = [f"Trigger: {trigger_type.replace('_', ' ').title()}"]
        events = context.get("recent_events", [])
        if events:
            recent = events[-3:]
            event_strs = [f"  - {e.get('event_type', 'unknown')}: {e.get('summary', '')}" for e in recent]
            parts.append("Recent events:\n" + "\n".join(event_strs))
        return "\n".join(parts)

    def _format_personality(self, traits: dict) -> str:
        if not traits:
            return "Balanced profile"
        lines = []
        for trait, value in traits.items():
            if trait in ("traits", "communication_style", "work_style"):
                continue
            if isinstance(value, (int, float)):
                label = "High" if value >= 70 else "Med" if value >= 40 else "Low"
                lines.append(f"  {trait.replace('_', ' ').title()}: {value:.0f}% ({label})")
        return "\n".join(lines) if lines else "Balanced profile"

    def _format_memories(self, memories: list) -> str:
        if not memories:
            return "  No relevant past experiences."
        lines = []
        for m in memories[:8]:
            importance = m.get("importance", "medium")
            marker = "!" if importance == "high" else "-" if importance == "low" else "~"
            lines.append(
                f"  [{marker}] {m.get('decision', m.get('title', 'unknown'))} "
                f"(confidence: {m.get('confidence', 0):.0%}, outcome: {m.get('outcome', m.get('actual_outcome', 'pending'))})"
            )
        return "\n".join(lines)

    def _format_constraints(self, constraints: dict) -> str:
        lines = []
        budget = constraints.get("budget", 0)
        lines.append(f"  Budget: {budget:.0f} NXC (cannot exceed this)")
        energy = constraints.get("energy", 50)
        lines.append(f"  Energy: {energy:.0f}% (below 10% = forced rest)")
        reputation = constraints.get("reputation", 0)
        lines.append(f"  Reputation: {reputation:.2f} (affects trust and opportunities)")
        return "\n".join(lines)

    def set_template(self, template: dict) -> None:
        self._template.update(template)

    def get_prompt_stats(self, prompt: str) -> dict:
        words = prompt.split()
        sections = [s for s in prompt.split("\n\n") if s.strip()]
        return {
            "word_count": len(words),
            "section_count": len(sections),
            "estimated_tokens": len(words) * 4 // 3,
            "char_count": len(prompt),
        }
