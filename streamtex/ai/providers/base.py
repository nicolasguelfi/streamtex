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
    """
    sizes: list[str]
    qualities: list[str]
    default_size: str = "1024x1024"
    default_quality: str = "standard"


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
