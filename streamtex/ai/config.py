"""AI image generation configuration — DI pattern (matches GSheetConfig, LinkConfig)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class AIImageConfig:
    """Configuration for AI image generation.

    Attributes:
        provider: Default provider name ("openai", "google", or "fal").
        default_size: Default image dimensions as "WxH".
        output_dir: Directory for saved images, relative to project root.
        auto_generate: When False (default), new images require a manual
            click on a "Generate" button. When True, images are generated
            automatically on first run (still cached on disk afterwards).
        api_keys: Optional dict of provider-specific API keys.
            Keys: "openai", "google", "fal". Values: API key strings.
            If not provided, keys are resolved from environment variables.
    """
    provider: str = "openai"
    default_size: str = "1024x1024"
    output_dir: str = "static/images/ai"
    auto_generate: bool = False
    api_keys: Dict[str, str] = field(default_factory=dict)

    def resolve_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """Resolve the API key for the given provider.

        Priority: explicit api_keys dict > STX_*_KEY env var > provider default env var.
        """
        p = provider or self.provider

        # 1. Explicit dict
        if p in self.api_keys:
            return self.api_keys[p]

        # 2. Environment variables
        env_map = {
            "openai": ("STX_OPENAI_API_KEY", "OPENAI_API_KEY"),
            "google": ("STX_GOOGLE_AI_KEY", "GOOGLE_AI_KEY"),
            "fal": ("STX_FAL_KEY", "FAL_KEY"),
        }
        for env_var in env_map.get(p, ()):
            val = os.environ.get(env_var)
            if val:
                return val

        return None


# ---------------------------------------------------------------------------
# Global singleton (same pattern as gsheet.py, link_config.py)
# ---------------------------------------------------------------------------

_ai_image_config: Optional[AIImageConfig] = None


def set_ai_image_config(config: Optional[AIImageConfig]) -> None:
    """Set the global AI image configuration. Call once at project startup."""
    global _ai_image_config
    _ai_image_config = config


def get_ai_image_config() -> Optional[AIImageConfig]:
    """Get the current AI image configuration."""
    return _ai_image_config
