"""Google Imagen provider (via google-genai SDK)."""

from __future__ import annotations

import logging
import os
from typing import Optional

from .base import AIImageProvider, AIImageResult, ModelCapabilities

logger = logging.getLogger(__name__)


class GoogleProvider(AIImageProvider):
    """Generate images using Google Imagen 4 (via the google-genai SDK)."""

    name = "google"

    @classmethod
    def available_models(cls) -> list[str]:
        return ["imagen-4.0-generate-001", "imagen-3.0-generate-002"]

    @classmethod
    def model_capabilities(cls, model: Optional[str] = None) -> ModelCapabilities:
        return ModelCapabilities(
            sizes=["1024x1024", "1024x1536", "1536x1024"],
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
                "  - api_key parameter in AIImageConfig or st_image()"
            )

        client = genai.Client(api_key=key)
        model_id = model or "imagen-4.0-generate-001"

        if base_image:
            from google.genai.types import EditImageConfig, RawReferenceImage
            response = client.models.edit_image(
                model=model_id,
                prompt=prompt,
                reference_images=[RawReferenceImage(
                    reference_image=genai.types.Image(image_bytes=base_image),
                    reference_id=0,
                )],
                config=EditImageConfig(number_of_images=1),
            )
        else:
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
