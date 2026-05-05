"""fal.ai Stable Diffusion v3.5 provider."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import AIImageProvider, AIImageResult, ModelCapabilities, SizeValidation

logger = logging.getLogger(__name__)

# fal.ai diffusion constraints (SD 3.5 Large, FLUX dev).  Each side must be a
# multiple of 64 pixels because the latent space is downsampled by the VAE.
# The total pixel count is capped to keep inference within the model's
# training distribution; going above produces tiling artefacts.
_FAL_SIDE_MIN = 256
_FAL_SIDE_MAX = 2048
_FAL_SIDE_MULTIPLE = 64
_FAL_MAX_PIXELS = 2_097_152  # 2 Mpx — matches SD 3.5 Large practical limit
_FAL_RATIO_WARN_THRESHOLD = 3.0  # log a quality warning above 3:1


def _round_to_multiple(value: int, multiple: int) -> int:
    """Round *value* to the nearest non-zero multiple of *multiple*."""
    rounded = round(value / multiple) * multiple
    return max(multiple, rounded)


class FalProvider(AIImageProvider):
    """Generate images using fal.ai (Stable Diffusion v3.5 Large)."""

    name = "fal"

    @classmethod
    def available_models(cls) -> list[str]:
        return ["fal-ai/stable-diffusion-v35-large", "fal-ai/flux/dev/image-to-image"]

    @classmethod
    def model_capabilities(cls, model: Optional[str] = None) -> ModelCapabilities:
        return ModelCapabilities(
            sizes=["512x512", "768x768", "1024x1024", "1024x1536", "1536x1024"],
            qualities=["standard"],
            default_size="1024x1024",
            default_quality="standard",
            supports_custom=True,
        )

    @classmethod
    def validate_size(
        cls, size: str, model: Optional[str] = None
    ) -> SizeValidation:
        """Validate / normalise a ``"WxH"`` size for fal.ai.

        Rules:
          - Each side must be in ``[256, 2048]``.
          - Each side is rounded to the nearest multiple of 64 (a SD/FLUX
            VAE constraint). The rounded value is reported via ``warning``.
          - Total pixels must not exceed 2 097 152 (~2 Mpx); above that,
            inference goes off-distribution and produces tiling.
          - Ratios above 3:1 are accepted but flagged as quality risks
            because diffusion models are trained near 1:1.

        Whitelisted sizes are passed through without any warning.
        """
        caps = cls.model_capabilities(model)
        if size in caps.sizes:
            return SizeValidation(valid=True, normalized=size)

        try:
            w_str, h_str = size.lower().split("x")
            width = int(w_str)
            height = int(h_str)
        except (ValueError, AttributeError):
            return SizeValidation(
                valid=False,
                error=f"Size must be formatted as 'WxH' (got {size!r}).",
            )

        if width <= 0 or height <= 0:
            return SizeValidation(
                valid=False,
                error="Width and height must be positive integers.",
            )

        if (
            width < _FAL_SIDE_MIN
            or height < _FAL_SIDE_MIN
            or width > _FAL_SIDE_MAX
            or height > _FAL_SIDE_MAX
        ):
            return SizeValidation(
                valid=False,
                error=(
                    f"Each side must be between {_FAL_SIDE_MIN} and "
                    f"{_FAL_SIDE_MAX} px (got {width}x{height})."
                ),
            )

        # Round to multiples of 64. Track whether we changed anything so the
        # editor can surface a "we adjusted your input" warning.
        rounded_w = _round_to_multiple(width, _FAL_SIDE_MULTIPLE)
        rounded_h = _round_to_multiple(height, _FAL_SIDE_MULTIPLE)
        rounded_w = max(_FAL_SIDE_MIN, min(_FAL_SIDE_MAX, rounded_w))
        rounded_h = max(_FAL_SIDE_MIN, min(_FAL_SIDE_MAX, rounded_h))

        if rounded_w * rounded_h > _FAL_MAX_PIXELS:
            return SizeValidation(
                valid=False,
                error=(
                    f"Total pixels {rounded_w * rounded_h:,} exceeds the "
                    f"{_FAL_MAX_PIXELS:,} px limit. Reduce one dimension."
                ),
            )

        warnings: list[str] = []
        if (rounded_w, rounded_h) != (width, height):
            warnings.append(
                f"Adjusted to {rounded_w}x{rounded_h} "
                f"(multiples of {_FAL_SIDE_MULTIPLE} required by SD/FLUX)."
            )

        ratio = max(rounded_w, rounded_h) / min(rounded_w, rounded_h)
        if ratio > _FAL_RATIO_WARN_THRESHOLD:
            warnings.append(
                f"Aspect ratio {ratio:.2f}:1 is extreme; diffusion models "
                "may produce duplicated subjects or composition artefacts."
            )

        return SizeValidation(
            valid=True,
            normalized=f"{rounded_w}x{rounded_h}",
            warning=" ".join(warnings) if warnings else None,
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
        try:
            import fal_client
        except ImportError:
            raise ImportError(
                "fal.ai provider requires the fal-client package.\n"
                "Install it with: uv add fal-client  (or: uv add 'streamtex[ai-fal]')"
            )

        key = api_key or os.environ.get("STX_FAL_KEY") or os.environ.get("FAL_KEY")
        if not key:
            raise ValueError(
                "fal.ai API key not found. Set one of:\n"
                "  - STX_FAL_KEY environment variable\n"
                "  - FAL_KEY environment variable\n"
                "  - api_key parameter in AIImageConfig or st_ai_image()"
            )

        # fal-client uses FAL_KEY env var internally
        os.environ["FAL_KEY"] = key

        model_id = model or "fal-ai/stable-diffusion-v35-large"

        # Parse size
        try:
            w, h = size.lower().split("x")
            width, height = int(w), int(h)
        except (ValueError, AttributeError):
            width, height = 1024, 1024

        arguments = {
            "prompt": prompt,
            "image_size": {"width": width, "height": height},
            "num_images": 1,
            **kwargs,
        }

        if base_image:
            import base64 as b64
            arguments["image_url"] = f"data:image/png;base64,{b64.b64encode(base_image).decode()}"
            # Use img2img model if default model is used
            if not model:
                model_id = "fal-ai/flux/dev/image-to-image"

        result = fal_client.subscribe(model_id, arguments=arguments)

        images = result.get("images", [])
        if not images:
            raise RuntimeError("fal.ai returned no images.")

        image_url = images[0].get("url", "")
        if not image_url:
            raise RuntimeError("fal.ai returned an image entry with no URL.")

        # Download the image
        import requests
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()

        # Detect format from content-type
        content_type = resp.headers.get("content-type", "image/png")
        fmt = "jpeg" if "jpeg" in content_type or "jpg" in content_type else "png"

        return AIImageResult(
            image_bytes=resp.content,
            format=fmt,
        )
