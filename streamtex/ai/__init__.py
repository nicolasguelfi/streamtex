"""StreamTeX AI image generation module.

Provides integration with external AI providers (OpenAI, Google Imagen,
fal.ai) for generating images and inserting them into StreamTeX presentations.
"""

from .config import AIImageConfig, get_ai_image_config, set_ai_image_config
from .generate import AIImageError, generate_image, is_cached
from .providers import get_available_models, get_model_capabilities, list_providers
from .providers.base import AIImageProvider, AIImageResult, ModelCapabilities

__all__ = [
    "AIImageConfig",
    "AIImageError",
    "AIImageProvider",
    "AIImageResult",
    "generate_image",
    "get_ai_image_config",
    "get_available_models",
    "get_model_capabilities",
    "is_cached",
    "ModelCapabilities",
    "list_providers",
    "set_ai_image_config",
]
