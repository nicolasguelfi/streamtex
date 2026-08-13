"""Native overlay slot for media elements.

``MediaOverlay`` describes a small badge ("pastille") rendered by the media
function itself, inside the final display box of the media — e.g. an
AI-transparency mark ("✦ AI").  The badge is *overlaid* on the media,
never burned into the pixels.

Used by :func:`streamtex.image.st_image` via its ``overlay=`` parameter.
Designed to be reused by a future ``st_video`` positioned container
(phase 2 — the video controls sit on the bottom edge, so ``top-right``
will be the recommended position there).
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass

# Corner → CSS offsets for the absolutely-positioned badge.
_POSITION_CSS = {
    "bottom-right": "right:8px; bottom:8px;",
    "top-right": "right:8px; top:8px;",
    "bottom-left": "left:8px; bottom:8px;",
    "top-left": "left:8px; top:8px;",
}

# Neutral default pill — projects override or extend it via MediaOverlay.css
# (appended after these declarations, so caller CSS wins in cascade order).
# line-height must be reset explicitly: the wrapper box uses line-height:0.
_BADGE_BASE_CSS = (
    "background:rgba(113,113,122,0.35); color:#fff; border-radius:9999px; "
    "padding:2px 8px; font-size:12px; line-height:1.2; white-space:nowrap; "
    "pointer-events:none; z-index:2;"
)

# margin declarations carrying an ``auto`` value (centering).  They must be
# transferred from the media style onto the wrapper — an auto margin left on
# the media alone stops centering once the media is boxed in a wrapper.
_MARGIN_AUTO_RE = re.compile(r"margin[a-z-]*\s*:\s*[^;]*\bauto\b[^;]*", re.IGNORECASE)


@dataclass(frozen=True)
class MediaOverlay:
    """Badge overlaid on a media element rendered by streamtex.

    :param text: Badge text (e.g. ``"✦ AI"``) — HTML-escaped at emission.
    :param position: Corner anchor: ``"bottom-right"`` (default),
        ``"top-right"``, ``"bottom-left"`` or ``"top-left"``.
    :param css: Extra CSS appended after the default pill style (so it
        overrides it in cascade order) — e.g. a project convention.
    :param aria_label: Accessible disclosure text (e.g. AI-transparency
        wording, art. 50 AI Act); emitted as ``aria-label`` when non-empty.
    """

    text: str
    position: str = "bottom-right"
    css: str = ""
    aria_label: str = ""

    def __post_init__(self):
        if self.position not in _POSITION_CSS:
            valid = ", ".join(sorted(_POSITION_CSS))
            raise ValueError(
                f"MediaOverlay.position must be one of: {valid} "
                f"(got {self.position!r})"
            )


def build_overlay_span(overlay: MediaOverlay) -> str:
    """Emit the badge ``<span class="stx-media-overlay">``.

    ``text`` and ``aria_label`` are HTML-escaped.  ``pointer-events:none``
    guarantees the badge never intercepts clicks (link wrapping stays fully
    functional).
    """
    badge_css = f"position:absolute; {_POSITION_CSS[overlay.position]} {_BADGE_BASE_CSS}"
    if overlay.css:
        badge_css = f"{badge_css} {overlay.css}"
    aria_attr = (
        f' aria-label="{html.escape(overlay.aria_label, quote=True)}"'
        if overlay.aria_label
        else ""
    )
    return (
        f'<span class="stx-media-overlay" role="note"{aria_attr} '
        f'style="{badge_css}">{html.escape(overlay.text)}</span>'
    )


def wrap_media_overlay(
    inner_html: str,
    overlay: MediaOverlay,
    *,
    width: str = "",
    caller_css: str = "",
) -> str:
    """Wrap *inner_html* in a ``stx-media-box`` and anchor the badge inside.

    The wrapper carries the resolved display *width* so that its box matches
    the media's real box even for percentage widths — a shrink-to-fit
    inline-block cannot follow a percentage-width child (the percentage
    would resolve against the intrinsic width, not the container).  The
    media inside is expected to fill the wrapper (``width: 100%``).

    Auto margins found in *caller_css* (centering) are transferred onto the
    wrapper, which then becomes the centered block.
    """
    auto_margins = [m.strip() for m in _MARGIN_AUTO_RE.findall(caller_css)]
    box_width = width or "auto"
    if auto_margins:
        # Centered media: the wrapper is the element the auto margins act on.
        if box_width == "auto":
            box_width = "fit-content"
        margins = " ".join(f"{m};" for m in auto_margins)
        box_css = (
            f"position:relative; display:block; width:{box_width}; "
            f"max-width:100%; line-height:0; {margins}"
        )
    else:
        box_css = (
            f"position:relative; display:inline-block; width:{box_width}; "
            f"max-width:100%; line-height:0;"
        )
    return (
        f'<span class="stx-media-box" style="{box_css}">'
        f"{inner_html}{build_overlay_span(overlay)}</span>"
    )
