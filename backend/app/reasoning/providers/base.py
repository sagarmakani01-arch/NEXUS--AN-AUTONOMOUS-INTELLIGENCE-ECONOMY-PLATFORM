import re
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...

    @property
    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> dict:
        """Return {"text": str, "tokens_used": int, "model": str, "latency_ms": float}"""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...

    def parse_json_response(self, text: str) -> dict:
        """Extract JSON from LLM response text, handling markdown code blocks and other wrapping."""
        if not text:
            return {}

        patterns = [
            r"```json\s*(.*?)\s*```",
            r"```\s*(.*?)\s*```",
            r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                candidate = match.strip()
                if not candidate.startswith("{"):
                    continue
                try:
                    return json.loads(candidate)
                except json.JSONDecodeError:
                    continue

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"raw_text": text}
