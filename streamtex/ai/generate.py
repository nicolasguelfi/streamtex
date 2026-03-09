"""Image generation orchestrator — cache, persist, and serve AI-generated images."""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Optional

from .config import AIImageConfig, get_ai_image_config
from .providers import get_provider
from .providers.base import AIImageResult

logger = logging.getLogger(__name__)


class AIImageError(Exception):
    """Raised when AI image generation fails."""


def _make_cache_key(prompt: str, provider: str, size: str, **kwargs) -> str:
    """Deterministic hash from generation parameters."""
    seed = kwargs.get("seed", "")
    quality = kwargs.get("quality", "standard")
    model = kwargs.get("model", "")
    payload = f"{provider}|{model}|{prompt}|{size}|{quality}|{seed}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _resolve_output_dir(config: AIImageConfig) -> str:
    """Resolve and create the output directory."""
    output_dir = config.output_dir
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.getcwd(), output_dir)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def _find_cached(output_dir: str, cache_key: str) -> Optional[str]:
    """Return the path of a cached image if it exists."""
    for ext in ("png", "jpeg", "jpg"):
        path = os.path.join(output_dir, f"{cache_key}.{ext}")
        if os.path.isfile(path):
            return path
    return None


def generate_image(
    prompt: str,
    *,
    provider: Optional[str] = None,
    size: Optional[str] = None,
    quality: str = "standard",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    config: Optional[AIImageConfig] = None,
    save: bool = True,
    **kwargs,
) -> str:
    """Generate an image and save it to disk. Returns the file path.

    If an image with the same parameters already exists in the cache
    directory, it is returned immediately without calling the API.

    Args:
        prompt: Text description of the image.
        provider: Provider name override (default: config.provider).
        size: Image size override (default: config.default_size).
        quality: Quality level ("standard" or "hd").
        api_key: API key override.
        model: Model identifier override.
        config: AIImageConfig override. If None, uses global config.
        save: Whether to persist the image to disk (default True).

    Returns:
        Absolute path to the generated (or cached) image file.

    Raises:
        AIImageError: On generation failure.
    """
    cfg = config or get_ai_image_config() or AIImageConfig()
    prov_name = provider or cfg.provider
    img_size = size or cfg.default_size
    key = api_key or cfg.resolve_api_key(prov_name)

    cache_key = _make_cache_key(
        prompt, prov_name, img_size,
        quality=quality, model=model or "", **kwargs,
    )

    # Check cache
    output_dir = _resolve_output_dir(cfg)
    cached = _find_cached(output_dir, cache_key)
    if cached:
        logger.debug("AI image cache hit: %s", cached)
        return cached

    # Generate
    try:
        prov = get_provider(prov_name)
        result: AIImageResult = prov.generate(
            prompt,
            size=img_size,
            quality=quality,
            api_key=key,
            model=model,
            **kwargs,
        )
    except Exception as e:
        raise AIImageError(f"Image generation failed ({prov_name}): {e}") from e

    # Save
    ext = result.format if result.format in ("png", "jpeg") else "png"
    file_path = os.path.join(output_dir, f"{cache_key}.{ext}")
    if save:
        with open(file_path, "wb") as f:
            f.write(result.image_bytes)
        logger.info("AI image saved: %s", file_path)

    return file_path


def is_cached(
    prompt: str,
    *,
    provider: Optional[str] = None,
    size: Optional[str] = None,
    quality: str = "standard",
    model: Optional[str] = None,
    config: Optional[AIImageConfig] = None,
    **kwargs,
) -> bool:
    """Check whether an image for the given parameters is already cached."""
    cfg = config or get_ai_image_config() or AIImageConfig()
    prov_name = provider or cfg.provider
    img_size = size or cfg.default_size
    cache_key = _make_cache_key(
        prompt, prov_name, img_size,
        quality=quality, model=model or "", **kwargs,
    )
    output_dir = _resolve_output_dir(cfg)
    return _find_cached(output_dir, cache_key) is not None
