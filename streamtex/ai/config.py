"""AI image generation configuration — DI pattern (matches GSheetConfig, LinkConfig)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _detect_project_root() -> str:
    """Detect the project root directory for a StreamTeX project.

    Resolution order:
    1. ``os.getcwd()`` if it contains ``book.py`` (most reliable in CLI
       and Docker contexts where the caller has already ``cd``'d into
       the project).
    2. Directory of ``__main__.__file__`` if it contains ``book.py``
       (works when Streamlit runs ``book.py`` directly).
    3. ``os.getcwd()`` as final fallback.
    """
    # 1. CWD is the strongest signal — CLI commands and Docker entrypoints
    #    always cd into the project before running.
    cwd = os.getcwd()
    if os.path.isfile(os.path.join(cwd, "book.py")):
        return cwd

    # 2. __main__.__file__ — works when Streamlit runs book.py directly
    #    (e.g. `streamlit run book.py`).  We only trust it if book.py
    #    lives in that directory; otherwise it's a CLI wrapper script.
    try:
        import __main__

        main_file = getattr(__main__, "__file__", None)
        if main_file:
            main_dir = os.path.dirname(os.path.abspath(main_file))
            if os.path.isfile(os.path.join(main_dir, "book.py")):
                return main_dir
    except Exception:
        logger.debug("Failed to detect project root from __main__.__file__", exc_info=True)

    # 3. Fallback to CWD even without book.py (e.g. tests, notebooks)
    return cwd


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
        save_format: Disk format for newly generated images. ``"webp"``
            (default) gives ~10× smaller files than PNG with no visible
            quality loss at ``save_quality=90``.  Set to ``"png"`` for
            lossless pixel-perfect output, or ``"jpeg"`` for photos.
        save_quality: Compression quality for lossy formats (WebP, JPEG).
            1–100, default 90.  Ignored when ``save_format="png"``.
        api_keys: Optional dict of provider-specific API keys.
            Keys: "openai", "google", "fal". Values: API key strings.
            If not provided, keys are resolved from environment variables.
        project_root: Absolute path to the project root. When ``None``
            (the default), the directory of the main Streamlit script
            (``book.py``) is used, so that relative paths like
            ``output_dir`` resolve correctly regardless of ``os.getcwd()``.
    """
    provider: str = "openai"
    default_size: str = "1024x1024"
    output_dir: str = "static/images/ai"
    auto_generate: bool = False
    save_format: str = "webp"
    save_quality: int = 90
    api_keys: Dict[str, str] = field(default_factory=dict)
    project_root: Optional[str] = None

    def get_project_root(self) -> str:
        """Return the project root, detecting it if not explicitly set."""
        return self.project_root or _detect_project_root()

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
