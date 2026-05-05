"""Provider registry — maps provider names to classes."""

from __future__ import annotations

from typing import Dict, List, Type

from .base import AIImageProvider, ModelCapabilities, SizeValidation

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


def get_available_models(provider_name: str) -> list[str]:
    """Return available models for the named provider."""
    _register_builtin_providers()
    cls = _PROVIDERS.get(provider_name)
    if cls is None:
        return []
    return cls.available_models()


def get_model_capabilities(
    provider_name: str, model: str | None = None
) -> ModelCapabilities:
    """Return supported sizes/qualities for *provider_name* and *model*.

    Falls back to generic defaults if the provider is unknown.
    """
    _register_builtin_providers()
    cls = _PROVIDERS.get(provider_name)
    if cls is None:
        return ModelCapabilities(
            sizes=["1024x1024"],
            qualities=["standard"],
        )
    return cls.model_capabilities(model)


def validate_size(
    provider_name: str, size: str, model: str | None = None
) -> SizeValidation:
    """Validate a ``"WxH"`` size against *provider_name* / *model*.

    Falls back to a generic reject when the provider is unknown.
    """
    _register_builtin_providers()
    cls = _PROVIDERS.get(provider_name)
    if cls is None:
        return SizeValidation(
            valid=False,
            error=f"Unknown provider {provider_name!r}.",
        )
    return cls.validate_size(size, model)
