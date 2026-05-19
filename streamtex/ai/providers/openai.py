"""OpenAI GPT-Image provider."""

from __future__ import annotations

import base64
import logging
import os
from typing import Optional

from .base import AIImageProvider, AIImageResult, ModelCapabilities

logger = logging.getLogger(__name__)


class OpenAIProvider(AIImageProvider):
    """Generate images using OpenAI's GPT-Image API (gpt-image-1 / dall-e-3)."""

    name = "openai"

    @classmethod
    def available_models(cls) -> list[str]:
        return ["gpt-image-1", "dall-e-3"]

    @classmethod
    def model_capabilities(cls, model: Optional[str] = None) -> ModelCapabilities:
        model = model or "gpt-image-1"
        if model == "gpt-image-1":
            return ModelCapabilities(
                sizes=["1024x1024", "1024x1536", "1536x1024"],
                qualities=["auto", "low", "medium", "high"],
                default_size="1536x1024",
                default_quality="auto",
            )
        # dall-e-3
        return ModelCapabilities(
            sizes=["1024x1024", "1024x1792", "1792x1024"],
            qualities=["standard", "hd"],
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
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "OpenAI provider requires the openai package.\n"
                "Install it with: uv add openai  (or: uv add 'streamtex[ai-openai]')"
            )

        key = api_key or os.environ.get("STX_OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise ValueError(
                "OpenAI API key not found. Set one of:\n"
                "  - STX_OPENAI_API_KEY environment variable\n"
                "  - OPENAI_API_KEY environment variable\n"
                "  - api_key parameter in AIImageConfig or st_image()"
            )

        client = OpenAI(api_key=key)
        model_id = model or "gpt-image-1"

        # gpt-image-1 uses "low"/"medium"/"high"/"auto" for quality;
        # dall-e-3 uses "standard"/"hd". Map common aliases.
        quality_map = {"standard": "auto", "hd": "high"}
        resolved_quality = quality_map.get(quality, quality)

        if base_image:
            # Image-to-image editing
            response = client.images.edit(
                model=model_id,
                image=base_image,
                prompt=prompt,
                size=size,
                n=1,
                **kwargs,
            )
        else:
            response = client.images.generate(
                model=model_id,
                prompt=prompt,
                size=size,
                quality=resolved_quality,
                n=1,
                **kwargs,
            )

        image_data = response.data[0]

        # GPT-Image returns base64 by default
        if hasattr(image_data, "b64_json") and image_data.b64_json:
            image_bytes = base64.b64decode(image_data.b64_json)
        elif hasattr(image_data, "url") and image_data.url:
            import requests
            resp = requests.get(image_data.url, timeout=60)
            resp.raise_for_status()
            image_bytes = resp.content
        else:
            raise RuntimeError("OpenAI response contained no image data.")

        revised = getattr(image_data, "revised_prompt", None)
        return AIImageResult(
            image_bytes=image_bytes,
            format="png",
            revised_prompt=revised,
        )
