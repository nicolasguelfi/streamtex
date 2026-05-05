"""Abstract base for AI image generation providers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class AIImageResult:
    """Result from an AI image generation call.

    Attributes:
        image_bytes: Raw image bytes (PNG or JPEG).
        format: Image format ("png" or "jpeg").
        revised_prompt: The prompt as revised/interpreted by the provider (if any).
    """
    image_bytes: bytes
    format: str = "png"
    revised_prompt: Optional[str] = None


@dataclass
class ModelCapabilities:
    """Supported sizes and quality levels for a specific model.

    Providers override :meth:`AIImageProvider.model_capabilities` to
    return accurate values per model.  The image editor uses this to
    populate size/quality dropdowns dynamically.

    Attributes:
        sizes: White-listed ``"WxH"`` strings exposed in the size dropdown.
        qualities: White-listed quality labels exposed in the quality dropdown.
        default_size: Pre-selected size when the editor opens.
        default_quality: Pre-selected quality when the editor opens.
        supports_custom: When True, the editor exposes a ``"Custom..."``
            entry that lets the user enter arbitrary width/height. The
            provider must also override :meth:`AIImageProvider.validate_size`
            to express its constraints (bounds, multiples, total pixels...).
    """
    sizes: list[str]
    qualities: list[str]
    default_size: str = "1024x1024"
    default_quality: str = "standard"
    supports_custom: bool = False


@dataclass
class SizeValidation:
    """Outcome of :meth:`AIImageProvider.validate_size`.

    Attributes:
        valid: True when the size can be sent to the provider as-is or
            after applying ``normalized``.
        normalized: Canonical ``"WxH"`` string the editor should use for
            generation. May differ from the input when the provider rounds
            dimensions to satisfy its constraints (e.g. multiples of 64).
        warning: Non-fatal advisory shown to the user (e.g. extreme aspect
            ratio likely to degrade quality). Generation can still proceed.
        error: Fatal explanation when ``valid`` is False (e.g. out of bounds,
            total pixels exceeded). Generation must be blocked.
    """
    valid: bool
    normalized: Optional[str] = None
    warning: Optional[str] = None
    error: Optional[str] = None


class AIImageProvider:
    """Base class for AI image generation providers.

    Subclasses must implement :meth:`generate`.
    """

    name: str = "base"

    @classmethod
    def available_models(cls) -> list[str]:
        """Return the list of supported model identifiers."""
        return []

    @classmethod
    def model_capabilities(cls, model: Optional[str] = None) -> ModelCapabilities:
        """Return supported sizes/qualities for *model*.

        Subclasses should override this with model-specific values.
        """
        return ModelCapabilities(
            sizes=["1024x1024"],
            qualities=["standard"],
        )

    @classmethod
    def validate_size(
        cls, size: str, model: Optional[str] = None
    ) -> SizeValidation:
        """Validate a ``"WxH"`` size string against this provider.

        Default implementation accepts only sizes listed in
        :meth:`model_capabilities`. Providers that support arbitrary
        dimensions (e.g. fal.ai) should override and set
        ``ModelCapabilities.supports_custom = True``.

        Args:
            size: User-entered ``"WxH"`` size, e.g. ``"1280x256"``.
            model: Optional model identifier. Constraints can vary per model.

        Returns:
            :class:`SizeValidation` describing whether the size is usable
            and what (if anything) the editor should normalise or warn about.
        """
        caps = cls.model_capabilities(model)
        if size in caps.sizes:
            return SizeValidation(valid=True, normalized=size)
        return SizeValidation(
            valid=False,
            error=(
                f"Size {size!r} is not supported by provider {cls.name!r}. "
                f"Allowed: {', '.join(caps.sizes)}."
            ),
        )

    def generate(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        quality: str = "standard",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_image: Optional[bytes] = None,
        **kwargs,
    ) -> AIImageResult:
        """Generate an image from *prompt*.

        Args:
            prompt: Text description of the image to generate.
            size: Image dimensions as "WxH" (e.g. "1024x1024").
            quality: Quality level ("standard" or "hd").
            api_key: Provider API key. If None, resolved from env vars.
            model: Model identifier override.
            base_image: Optional image bytes to use as a starting point (image-to-image editing).

        Returns:
            AIImageResult with the generated image bytes.

        Raises:
            AIImageError: On generation failure.
        """
        raise NotImplementedError
