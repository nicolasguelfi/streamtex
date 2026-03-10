"""Image metadata management — JSON sidecar files for version tracking."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class ImageMetadata:
    """Metadata for a managed image.

    Attributes:
        name: Semantic name (e.g. "hero_intro").
        version: Current version number.
        timestamp: ISO 8601 creation time.
        source_type: "local", "url", or "ai_generated".
        original_path: Original source path or URL.
        prompt: AI prompt (None for non-AI images).
        provider: AI provider name (None for non-AI images).
        model: AI model identifier (None for non-AI images).
        size: AI generation size (None for non-AI images).
        quality: AI generation quality (None for non-AI images).
        base_image: Path to base image used for img2img (None if from scratch).
        revised_prompt: Provider-revised prompt (None if not available).
    """
    name: str
    version: int = 1
    timestamp: str = ""
    source_type: str = "local"  # "local", "url", "ai_generated"
    original_path: str = ""
    prompt: Optional[str] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    size: Optional[str] = None
    quality: Optional[str] = None
    base_image: Optional[str] = None
    revised_prompt: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


def save_metadata(meta: ImageMetadata, json_path: str) -> None:
    """Write metadata to a JSON sidecar file."""
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(asdict(meta), f, indent=2, ensure_ascii=False)


def load_metadata(json_path: str) -> Optional[ImageMetadata]:
    """Load metadata from a JSON sidecar file. Returns None if not found."""
    if not os.path.isfile(json_path):
        return None
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    return ImageMetadata(**data)


def metadata_path_for(image_path: str) -> str:
    """Return the JSON sidecar path for an image path.

    Example: "static/images/managed/hero.png" -> "static/images/managed/hero.json"
    """
    root, _ = os.path.splitext(image_path)
    return root + ".json"
