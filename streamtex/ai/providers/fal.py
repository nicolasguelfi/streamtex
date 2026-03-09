"""fal.ai Stable Diffusion v3.5 provider."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import AIImageProvider, AIImageResult

logger = logging.getLogger(__name__)


class FalProvider(AIImageProvider):
    """Generate images using fal.ai (Stable Diffusion v3.5 Large)."""

    name = "fal"

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
