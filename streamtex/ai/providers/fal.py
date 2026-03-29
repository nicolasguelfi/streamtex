"""fal.ai Stable Diffusion v3.5 provider."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import AIImageProvider, AIImageResult, ModelCapabilities

logger = logging.getLogger(__name__)


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
