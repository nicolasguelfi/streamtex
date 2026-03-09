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


class AIImageProvider:
    """Base class for AI image generation providers.

    Subclasses must implement :meth:`generate`.
    """

    name: str = "base"

    def generate(
        self,
        prompt: str,
        *,
        size: str = "1024x1024",
        quality: str = "standard",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs,
    ) -> AIImageResult:
        """Generate an image from *prompt*.

        Args:
            prompt: Text description of the image to generate.
            size: Image dimensions as "WxH" (e.g. "1024x1024").
            quality: Quality level ("standard" or "hd").
            api_key: Provider API key. If None, resolved from env vars.
            model: Model identifier override.

        Returns:
            AIImageResult with the generated image bytes.

        Raises:
            AIImageError: On generation failure.
        """
        raise NotImplementedError
