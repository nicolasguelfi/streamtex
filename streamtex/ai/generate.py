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
    has_base = "base" if kwargs.get("base_image") else ""
    payload = f"{provider}|{model}|{prompt}|{size}|{quality}|{seed}|{has_base}"
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _resolve_output_dir(config: AIImageConfig) -> str:
    """Resolve and create the output directory.

    Relative paths are resolved against the project root (the directory
    containing the main ``book.py``), **not** ``os.getcwd()``.
    """
    output_dir = config.output_dir
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(config.get_project_root(), output_dir)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def _find_cached(output_dir: str, cache_key: str) -> Optional[str]:
    """Return the path of a cached image if it exists."""
    for ext in ("webp", "png", "jpeg", "jpg"):
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
    base_image: Optional[bytes] = None,
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
            base_image=base_image,
            **kwargs,
        )
    except Exception as e:
        raise AIImageError(f"Image generation failed ({prov_name}): {e}") from e

    # Transcode to configured save_format (default: webp for ~10× smaller files)
    image_bytes = result.image_bytes
    target_fmt = cfg.save_format.lower()

    if target_fmt in ("webp", "jpeg") and target_fmt != result.format:
        try:
            import io

            from PIL import Image

            img = Image.open(io.BytesIO(image_bytes))
            if target_fmt == "jpeg" and img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            buf = io.BytesIO()
            pil_fmt = "WEBP" if target_fmt == "webp" else "JPEG"
            img.save(buf, format=pil_fmt, quality=cfg.save_quality)
            image_bytes = buf.getvalue()
            ext = target_fmt
            logger.debug("Transcoded to %s (quality=%d)", ext, cfg.save_quality)
        except (ImportError, Exception) as exc:
            logger.debug("Transcoding skipped (%s) — keeping original %s format", exc, result.format)
            ext = result.format if result.format in ("png", "jpeg") else "png"
    else:
        ext = target_fmt if target_fmt in ("png", "jpeg", "webp") else result.format

    # Save
    file_path = os.path.join(output_dir, f"{cache_key}.{ext}")
    if save:
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        logger.info("AI image saved: %s (%d bytes)", file_path, len(image_bytes))

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
