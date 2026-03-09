"""Provider registry — maps provider names to classes."""

from __future__ import annotations

from typing import Dict, List, Type

from .base import AIImageProvider

_PROVIDERS: Dict[str, Type[AIImageProvider]] = {}


def _register_builtin_providers() -> None:
    """Lazily register built-in providers on first access."""
    if _PROVIDERS:
        return
    from .fal import FalProvider
    from .google import GoogleProvider
    from .openai import OpenAIProvider
    _PROVIDERS["openai"] = OpenAIProvider
    _PROVIDERS["google"] = GoogleProvider
    _PROVIDERS["fal"] = FalProvider


def get_provider(name: str) -> AIImageProvider:
    """Return an instance of the named provider.

    Raises:
        ValueError: If *name* is not a registered provider.
    """
    _register_builtin_providers()
    cls = _PROVIDERS.get(name)
    if cls is None:
        available = ", ".join(sorted(_PROVIDERS))
        raise ValueError(
            f"Unknown AI image provider: {name!r}. "
            f"Available providers: {available}"
        )
    return cls()


def list_providers() -> List[str]:
    """Return the names of all registered providers."""
    _register_builtin_providers()
    return sorted(_PROVIDERS)
