"""Slide break — presentation-mode section separator."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import streamlit as st

from .export import _render
from .marker import st_marker
from .spacing import (
    Spacing,
    consume_block_top_injected,
    resolve_section_spacing,
    set_section_horizontal,
    set_section_zoom,
)


class SlideBreakMode(Enum):
    """Display mode for slide breaks.

    Controls what is rendered by ``st_slide_break()``:

    - ``FULL`` — rule + spacer + marker (default, presentation mode).
    - ``RULE_ONLY`` — horizontal rule only, no vertical space.
    - ``SPACER_ONLY`` — vertical space only, no visible rule.
    - ``MARKER_ONLY`` — hidden navigation marker only (PageDown stops).
    - ``HIDDEN`` — nothing rendered at all (disabled).
    """

    FULL = "full"
    RULE_ONLY = "rule_only"
    SPACER_ONLY = "spacer_only"
    MARKER_ONLY = "marker_only"
    HIDDEN = "hidden"


@dataclass
class SlideBreakConfig:
    """Configuration for st_slide_break() separators.

    Customize the horizontal rule appearance and vertical spacing
    used between presentation sections.

    Example::

        from streamtex import SlideBreakConfig, SlideBreakMode, set_slide_break_config

        set_slide_break_config(SlideBreakConfig(
            mode=SlideBreakMode.FULL,
            thickness="2px",
            color="79, 172, 254",
            opacity=0.5,
            space="80vh",
        ))
    """

    mode: SlideBreakMode = SlideBreakMode.FULL
    """Display mode (FULL, RULE_ONLY, SPACER_ONLY, MARKER_ONLY, HIDDEN)."""

    space: str = "5vh"
    """Vertical space after the rule (CSS value). 100vh = one full viewport."""

    space_before: str = "0vh"
    """Vertical space before the rule (CSS value). Rendered as a spacer div."""

    rule_margin_top: str = "5em"
    """Space before the horizontal rule (CSS value, e.g. "2em", "20px")."""

    rule_margin_bottom: str = "5em"
    """Space after the horizontal rule (CSS value, e.g. "2em", "20px")."""

    thickness: str = "1px"
    """Horizontal rule thickness (CSS value)."""

    color: str = "128, 128, 128"
    """Rule color as RGB values (e.g. "128, 128, 128")."""

    opacity: float = 0.5
    """Rule opacity from 0.0 (invisible) to 1.0 (fully opaque)."""

    marker: bool = True
    """Create a navigation marker so PageDown stops at this break."""

    marker_hidden: bool = True
    """When True, the marker is hidden (counter only, not in popup).
    When False, the marker is visible in the popup marker list."""

    fullscreen: bool = False
    """When True, force space='100vh' so each slide fills the viewport."""

    spacing: Spacing | None = None
    """Section spacing override for this specific slide break.
    When None, inherits from block-level or global section spacing."""


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
# Session state keys (used by add_slide_break_options)
# ---------------------------------------------------------------------------

_BREAK_ENABLED_KEY = "_stx_slide_break_enabled"
_BREAK_MODE_KEY = "_stx_slide_break_mode"
_BREAK_BEFORE_KEY = "_stx_slide_break_before"
_BREAK_AFTER_KEY = "_stx_slide_break_after"

# Mode label → SlideBreakMode mapping for the sidebar selectbox
_MODE_LABELS = {
    "Full": SlideBreakMode.FULL,
    "Rule only": SlideBreakMode.RULE_ONLY,
    "Spacer only": SlideBreakMode.SPACER_ONLY,
    "Marker only": SlideBreakMode.MARKER_ONLY,
    "Hidden": SlideBreakMode.HIDDEN,
}



# ---------------------------------------------------------------------------
# Sidebar widget (prop 5)
# ---------------------------------------------------------------------------

def _parse_space_vh(space: str) -> int:
    """Extract the integer vh value from a CSS space string like '60vh'."""
    s = space.strip().lower()
    if s.endswith("vh"):
        s = s[:-2]
    try:
        return int(float(s))
    except (ValueError, TypeError):
        return 60


def add_slide_break_options(
    default_enabled: bool = True,
    default_mode: Optional[SlideBreakMode] = None,
    default_space: Optional[int] = None,
    default_before: Optional[int] = None,
    default_after: Optional[int] = None,
    container=None,
) -> None:
    """Add slide break controls to the sidebar.

    Mirrors the pattern of :func:`add_zoom_options`: the presenter can
    toggle breaks on/off, choose a display style, and adjust spacing
    before and after the horizontal rule.
    Values are stored in session state and read directly by
    :func:`st_slide_break` on each render (Python-side control).

    Call once in ``book.py``, alongside ``add_zoom_options()``.

    :param default_enabled: Initial toggle state (default True).
    :param default_mode: Initial display mode.  When ``None`` (the
        default), the value is read from the global
        :class:`SlideBreakConfig` set by ``set_slide_break_config()``.
    :param default_space: Deprecated — use *default_after* instead.
        When set (and *default_after* is ``None``), used as the
        initial "After" value for backward compatibility.
    :param default_before: Initial "Before" spacing in vh.  When ``None``,
        the value is read from the global :class:`SlideBreakConfig`.
    :param default_after: Initial "After" spacing in vh.  When ``None``,
        the value is read from the global :class:`SlideBreakConfig`.
    :param container: Streamlit container to render into (default: sidebar).
    """
    if default_mode is None:
        default_mode = _config.mode
    if default_before is None:
        default_before = _parse_space_vh(_config.space_before)
    if default_after is None:
        if default_space is not None:
            default_after = default_space
        else:
            default_after = _parse_space_vh(_config.space)

    if _BREAK_ENABLED_KEY not in st.session_state:
        st.session_state[_BREAK_ENABLED_KEY] = default_enabled
    if _BREAK_MODE_KEY not in st.session_state:
        st.session_state[_BREAK_MODE_KEY] = next(
            k for k, v in _MODE_LABELS.items() if v == default_mode
        )
    if _BREAK_BEFORE_KEY not in st.session_state:
        st.session_state[_BREAK_BEFORE_KEY] = default_before
    if _BREAK_AFTER_KEY not in st.session_state:
        st.session_state[_BREAK_AFTER_KEY] = default_after

    ctx = container if container is not None else st.sidebar
    ctx.toggle("Slide breaks", key=_BREAK_ENABLED_KEY)
    if st.session_state[_BREAK_ENABLED_KEY]:
        ctx.selectbox(
            "Style",
            options=list(_MODE_LABELS.keys()),
            key=_BREAK_MODE_KEY,
        )
        ctx.number_input(
            "Before (vh)",
            min_value=0,
            max_value=100,
            step=10,
            key=_BREAK_BEFORE_KEY,
        )
        ctx.number_input(
            "After (vh)",
            min_value=0,
            max_value=100,
            step=10,
            key=_BREAK_AFTER_KEY,
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def _effective_config(
    config: Optional[SlideBreakConfig],
) -> tuple[SlideBreakConfig, bool]:
    """Return the effective config after sidebar overrides.

    CSS variables don't propagate across Streamlit Shadow DOM boundaries,
    so the sidebar widget values are read directly from session state and
    applied as Python-side overrides.

    Returns ``(effective_config, enabled)`` where *enabled* is False when
    the sidebar toggle is off.
    """
    cfg = config or _config
    enabled_val = st.session_state.get(_BREAK_ENABLED_KEY)
    if enabled_val is None:
        # No sidebar widget active — use config as-is
        return cfg, True

    if not enabled_val:
        return cfg, False

    # Override mode and before/after from sidebar
    mode_label = st.session_state.get(_BREAK_MODE_KEY, "Full")
    sidebar_mode = _MODE_LABELS.get(mode_label, cfg.mode)
    before_vh = st.session_state.get(_BREAK_BEFORE_KEY, 0)
    after_vh = st.session_state.get(_BREAK_AFTER_KEY, 5)

    return SlideBreakConfig(
        mode=sidebar_mode,
        space=f"{after_vh}vh",
        space_before=f"{before_vh}vh",
        rule_margin_top=cfg.rule_margin_top,
        rule_margin_bottom=cfg.rule_margin_bottom,
        thickness=cfg.thickness,
        color=cfg.color,
        opacity=cfg.opacity,
        marker=cfg.marker,
        marker_hidden=cfg.marker_hidden,
        fullscreen=cfg.fullscreen,
        spacing=cfg.spacing,
    ), True


def st_slide_break(
    marker_label: str = "",
    config: Optional[SlideBreakConfig] = None,
    spacing: Optional[Spacing] = None,
    zoom: Optional[int] = None,
    marker_hidden: Optional[bool] = None,
) -> None:
    """Presentation section break: styled rule + viewport spacer + marker.

    Inserts a horizontal rule followed by a large vertical space so that
    the next section starts off-screen. By default, places a navigation
    marker so PageUp/PageDown stops here.

    When the sidebar widget :func:`add_slide_break_options` is active, its
    values (toggle, mode, spacing) override the static config directly
    via Python-side session state — no CSS variable propagation needed.

    Args:
        marker_label: Label for the marker. Auto-generated if empty.
        config: Per-call config override. Falls back to the global config
                set by set_slide_break_config().
        spacing: Per-call section spacing override.  Takes precedence over
                 ``config.spacing`` and all other levels.
        zoom: Shortcut for ``spacing=Spacing(zoom=N)``.  Sets the CSS zoom
              percentage for all content until the next slide break.
              ``100`` = normal, ``75`` = 75%, ``150`` = 150%.
              When both *zoom* and *spacing.zoom* are set, *zoom* wins.
        marker_hidden: Per-call override for marker visibility.  When
              ``None`` (the default), uses ``config.marker_hidden``.
    """
    from .space import st_space

    cfg, enabled = _effective_config(config)

    # Deactivate horizontal spacing and zoom from the previous section
    set_section_horizontal(None)
    set_section_zoom(None)

    # Merge zoom= shortcut into call-site spacing
    call_site = spacing or cfg.spacing
    if zoom is not None:
        if call_site is not None:
            call_site = Spacing(
                top=call_site.top, bottom=call_site.bottom,
                left=call_site.left, right=call_site.right,
                width=call_site.width, zoom=zoom,
            )
        else:
            call_site = Spacing(zoom=zoom)

    # Resolve section spacing: direct param > config.spacing > block > profile > global
    effective_spacing = resolve_section_spacing(
        call_site=call_site,
    )

    # Inject section.bottom before the break visual (space after previous section)
    if effective_spacing.bottom is not None:
        st_space("v", effective_spacing.bottom)

    if not enabled or cfg.mode == SlideBreakMode.HIDDEN:
        # Even when hidden, fullscreen marker is still needed for navigation
        if cfg.fullscreen and cfg.marker:
            st_marker(marker_label, hidden=True)
        # Still inject section.top after the break (even if visual is hidden)
        if not consume_block_top_injected() and effective_spacing.top is not None:
            st_space("v", effective_spacing.top)
        _activate_section_horizontal(effective_spacing)
        return

    # Fullscreen mode forces 100vh spacing
    effective_space = "100vh" if cfg.fullscreen else cfg.space
    effective_space_before = cfg.space_before

    rule_css = (
        f"border: none; "
        f"border-top: {cfg.thickness} solid "
        f"rgba({cfg.color}, {cfg.opacity}); "
        f"margin-top: {cfg.rule_margin_top}; margin-bottom: {cfg.rule_margin_bottom};"
    )
    spacer_before_css = f"height: {effective_space_before};"
    spacer_css = f"height: {effective_space};"

    show_rule = cfg.mode in (SlideBreakMode.FULL, SlideBreakMode.RULE_ONLY)
    show_spacer = cfg.mode in (SlideBreakMode.FULL, SlideBreakMode.SPACER_ONLY)

    # Before-spacer: rendered before the rule when space_before > 0
    if show_spacer and effective_space_before and effective_space_before != "0vh":
        _render(f'<div class="stx-slide-break-spacer-before" style="{spacer_before_css}"></div>')
    if show_rule:
        _render(f'<hr class="stx-slide-break-rule" style="{rule_css}">')
    if show_spacer:
        _render(f'<div class="stx-slide-break-spacer" style="{spacer_css}"></div>')
    if cfg.marker and cfg.mode != SlideBreakMode.HIDDEN:
        _hidden = marker_hidden if marker_hidden is not None else cfg.marker_hidden
        st_marker(marker_label, hidden=_hidden)

    # Inject section.top after the break visual (space before next section)
    # Skip if block.top was already injected for this block (first break)
    if not consume_block_top_injected() and effective_spacing.top is not None:
        st_space("v", effective_spacing.top)

    # Activate section-level horizontal spacing for subsequent _render() calls
    _activate_section_horizontal(effective_spacing)


# ---------------------------------------------------------------------------
# Section-level horizontal spacing (Phase 3)
# ---------------------------------------------------------------------------

def _close_section_wrapper_if_open() -> None:
    """Deactivate section-level horizontal spacing and zoom.

    Called by ``st_book`` after each ``build()`` to ensure cleanup.
    """
    set_section_horizontal(None)
    set_section_zoom(None)


def _activate_section_horizontal(spacing: Spacing) -> None:
    """Activate horizontal padding and zoom on all subsequent ``_render()`` calls.

    When ``left`` or ``right`` is set, ``st_html()`` in ``export.py``
    wraps each HTML fragment with a ``<div>`` that applies the padding.
    When ``zoom`` is set, a CSS ``zoom`` property is added to the wrapper.
    The state is cleared at the next ``st_slide_break`` or block end.
    """
    has_horizontal = (
        spacing.left is not None
        or spacing.right is not None
    )
    if has_horizontal:
        set_section_horizontal(spacing)
    else:
        set_section_horizontal(None)

    if spacing.zoom is not None:
        set_section_zoom(spacing.zoom)
    else:
        set_section_zoom(None)
