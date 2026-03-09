"""Google Imagen provider (via google-genai SDK)."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import AIImageProvider, AIImageResult

logger = logging.getLogger(__name__)


class GoogleProvider(AIImageProvider):
    """Generate images using Google Imagen 4 (via the google-genai SDK)."""

    name = "google"

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
            from google import genai
        except ImportError:
            raise ImportError(
                "Google Imagen provider requires the google-genai package.\n"
                "Install it with: uv add google-genai  (or: uv add 'streamtex[ai-google]')"
            )

        key = api_key or os.environ.get("STX_GOOGLE_AI_KEY") or os.environ.get("GOOGLE_AI_KEY")
        if not key:
            raise ValueError(
                "Google AI API key not found. Set one of:\n"
                "  - STX_GOOGLE_AI_KEY environment variable\n"
                "  - GOOGLE_AI_KEY environment variable\n"
                "  - api_key parameter in AIImageConfig or st_ai_image()"
            )

        client = genai.Client(api_key=key)
        model_id = model or "imagen-4.0-generate-001"

        response = client.models.generate_images(
            model=model_id,
            prompt=prompt,
            config=genai.types.GenerateImagesConfig(
                number_of_images=1,
            ),
        )

        if not response.generated_images:
            raise RuntimeError("Google Imagen returned no images.")

        image = response.generated_images[0].image
        image_bytes = image.image_bytes

        return AIImageResult(
            image_bytes=image_bytes,
            format="png",
        )
