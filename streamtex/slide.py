"""Slide break — presentation-mode section separator."""

from dataclasses import dataclass
from typing import Optional

from .export import _render
from .marker import st_marker


@dataclass
class SlideBreakConfig:
    """Configuration for st_slide_break() separators.

    Customize the horizontal rule appearance and vertical spacing
    used between presentation sections.

    Example::

        from streamtex import SlideBreakConfig, set_slide_break_config

        set_slide_break_config(SlideBreakConfig(
            thickness="2px",
            color="79, 172, 254",
            opacity=0.5,
            space="80vh",
        ))
    """

    space: str = "60vh"
    """Vertical space after the rule (CSS value). 100vh = one full viewport."""

    thickness: str = "1px"
    """Horizontal rule thickness (CSS value)."""

    color: str = "128, 128, 128"
    """Rule color as RGB values (e.g. "128, 128, 128")."""

    opacity: float = 0.3
    """Rule opacity from 0.0 (invisible) to 1.0 (fully opaque)."""

    marker: bool = True
    """Create a hidden navigation marker so PageDown stops at this break."""


# ---------------------------------------------------------------------------
# Global config — overridable per project via set_slide_break_config()
# ---------------------------------------------------------------------------

_config: SlideBreakConfig = SlideBreakConfig()


def set_slide_break_config(config: SlideBreakConfig) -> None:
    """Set the global slide break configuration.

    Call once in your project's helpers.py or book.py to customize
    all st_slide_break() calls project-wide.
    """
    global _config
    _config = config


def get_slide_break_config() -> SlideBreakConfig:
    """Return the current global slide break config."""
    return _config


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def st_slide_break(
    marker_label: str = "",
    config: Optional[SlideBreakConfig] = None,
) -> None:
    """Presentation section break: styled rule + viewport spacer + hidden marker.

    Inserts a horizontal rule followed by a large vertical space so that
    the next section starts off-screen. By default, places a hidden
    navigation marker so PageUp/PageDown stops here without appearing
    in the sidebar marker list or TOC.

    Args:
        marker_label: Label for the hidden marker. Auto-generated if empty.
        config: Per-call config override. Falls back to the global config
                set by set_slide_break_config().
    """
    cfg = config or _config
    rule_css = (
        f"border: none; "
        f"border-top: {cfg.thickness} solid rgba({cfg.color}, {cfg.opacity}); "
        f"margin: 0.5em 0;"
    )
    _render(f'<hr class="stx-slide-break-rule" style="{rule_css}">')
    _render(f'<div class="stx-slide-break-spacer" style="height: {cfg.space};"></div>')
    if cfg.marker:
        st_marker(marker_label, hidden=True)
