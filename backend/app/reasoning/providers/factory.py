import os
from typing import Optional

from .base import BaseProvider
from .deterministic import DeterministicProvider


_PROVIDER_CACHE: dict[str, BaseProvider] = {}


def _get_deterministic() -> DeterministicProvider:
    if "deterministic" not in _PROVIDER_CACHE:
        _PROVIDER_CACHE["deterministic"] = DeterministicProvider()
    return _PROVIDER_CACHE["deterministic"]


def _try_openai() -> Optional[BaseProvider]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(api_key=api_key)
    except ImportError:
        return None


def _try_anthropic() -> Optional[BaseProvider]:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(api_key=api_key)
    except ImportError:
        return None


def _try_google() -> Optional[BaseProvider]:
    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    try:
        from .google_provider import GoogleProvider

        return GoogleProvider(api_key=api_key)
    except ImportError:
        return None


def _try_local() -> Optional[BaseProvider]:
    base_url = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434")
    try:
        from .local_provider import LocalProvider

        return LocalProvider(base_url=base_url)
    except ImportError:
        return None


_FATORY_MAP = {
    "openai": _try_openai,
    "anthropic": _try_anthropic,
    "google": _try_google,
    "local": _try_local,
}


def get_provider(name: str = "deterministic") -> BaseProvider:
    name = name.lower().strip()

    if name == "deterministic":
        return _get_deterministic()

    if name in _PROVIDER_CACHE:
        cached = _PROVIDER_CACHE[name]
        if cached.is_available:
            return cached
        del _PROVIDER_CACHE[name]

    factory = _FATORY_MAP.get(name)
    if factory is None:
        return _get_deterministic()

    provider = factory()
    if provider is None or not provider.is_available:
        return _get_deterministic()

    _PROVIDER_CACHE[name] = provider
    return provider
