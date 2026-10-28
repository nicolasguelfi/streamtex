"""Slide break — presentation-mode section separator."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import streamlit as st

from .export import _render
from .marker import MarkerRoles, marker_slide_boundary, st_marker
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

    marker: bool | MarkerRoles = True
    """The break's navigation marker. ``True`` = a stop, listed unless
    ``marker_hidden``; ``False`` = no marker (the break still starts a new
    slide); a ``MarkerRoles`` = exactly these roles (its ``toc_lvl`` needs a
    ``marker_label``)."""

    marker_hidden: bool = True
    """Shortcut for the *listed* role when ``marker`` is ``True``: True = a
    stop that is not listed (counter only, not in the popup), False = also
    listed in the marker list."""

    fullscreen: bool = False
    """When True, force space='100vh' so each slide fills the viewport."""

    spacing: Spacing | None = None
    """Section spacing override for this specific slide break.
    When None, inherits from block-level or global section spacing."""


# ---------------------------------------------------------------------------
# Global config — overridable per project via set_slide_break_config()
# ---------------------------------------------------------------------------

_config: SlideBreakConfig = SlideBreakConfig()


def _in_session() -> bool:
    """True inside a Streamlit script run (a viewer's session)."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx(suppress_warning=True) is not None
    except Exception:  # noqa: BLE001 — bare mode / Streamlit drift
        return False


_BREAK_CONFIG_KEY = "_stx_slide_break_config"


def set_slide_break_config(config: SlideBreakConfig) -> None:
    """Set the slide break configuration of the module.

    Call once in ``book.py`` (it runs at every rerun of every session).
    Stored per session (#122): two modules, or two sessions, served by one
    process never overwrite each other. Outside a session (tests, the
    ``stx`` CLIs) a process-wide fallback is used.
    """
    global _config
    if _in_session():
        st.session_state[_BREAK_CONFIG_KEY] = config
    else:
        _config = config


def get_slide_break_config() -> SlideBreakConfig:
    """Return the slide break config of this session (else the process-wide one)."""
    if _in_session():
        cfg = st.session_state.get(_BREAK_CONFIG_KEY)
        if cfg is not None:
            return cfg
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
        default_mode = get_slide_break_config().mode
    if default_before is None:
        default_before = _parse_space_vh(get_slide_break_config().space_before)
    if default_after is None:
        if default_space is not None:
            default_after = default_space
        else:
            default_after = _parse_space_vh(get_slide_break_config().space)

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
    cfg = config or get_slide_break_config()
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
    *,
    marker: bool | MarkerRoles | None = None,
    _marker_key: Optional[str] = None,
    _force_marker: bool = False,
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
        marker_hidden: Per-call override for the *listed* role of a
              ``True`` marker.  When ``None`` (the default), uses
              ``config.marker_hidden``.
        marker: Per-call marker, wins over ``config.marker``: ``True``,
              ``False`` (no marker) or a ``MarkerRoles`` (see
              ``SlideBreakConfig.marker``).

    Every call starts a new slide, with or without a marker (#116 §4.6).
    """
    from .space import st_space

    cfg, enabled = _effective_config(config)
    marker_slide_boundary("break")
    roles = _break_marker_roles(cfg, marker, marker_hidden)

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

    # A break at the head of a page (paginated view, pages following the
    # tree, #121) draws neither its rule nor its spacers; its marker, the
    # spacing and the zoom it activates are kept.
    from . import pagewalk
    head_of_page = pagewalk.suppress_break()

    # Inject section.bottom before the break visual (space after previous section)
    if effective_spacing.bottom is not None and not head_of_page:
        st_space("v", effective_spacing.bottom)

    if not enabled or cfg.mode == SlideBreakMode.HIDDEN:
        # Even when hidden, fullscreen marker is still needed for navigation
        if roles is not None and (cfg.fullscreen or _force_marker):
            st_marker(marker_label, key=_marker_key, roles=roles, _origin="break")
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

    show_rule = cfg.mode in (SlideBreakMode.FULL, SlideBreakMode.RULE_ONLY) and not head_of_page
    show_spacer = cfg.mode in (SlideBreakMode.FULL, SlideBreakMode.SPACER_ONLY) and not head_of_page

    # Before-spacer: rendered before the rule when space_before > 0
    if show_spacer and effective_space_before and effective_space_before != "0vh":
        _render(f'<div class="stx-slide-break-spacer-before" style="{spacer_before_css}"></div>')
    if show_rule:
        _render(f'<hr class="stx-slide-break-rule" style="{rule_css}">')
    if show_spacer:
        _render(f'<div class="stx-slide-break-spacer" style="{spacer_css}"></div>')
    if roles is not None and (cfg.mode != SlideBreakMode.HIDDEN or _force_marker):
        st_marker(marker_label, key=_marker_key, roles=roles, _origin="break")

    # Inject section.top after the break visual (space before next section)
    # Skip if block.top was already injected for this block (first break)
    if not consume_block_top_injected() and effective_spacing.top is not None:
        st_space("v", effective_spacing.top)

    # Activate section-level horizontal spacing for subsequent _render() calls
    _activate_section_horizontal(effective_spacing)


def _standard_break() -> None:
    """The standard break between two included items (#118): no marker.

    The module's break settings (``set_slide_break_config``, read at call
    time) and the sidebar options apply as to any break; it starts a new
    slide but places no stop — the next item brings its own marker. Used by
    ``st_include(break_before=True)``, ``st_sequence`` and, in exports,
    between two book entries.
    """
    st_slide_break(marker=False)


def _break_marker_roles(cfg: SlideBreakConfig, marker: bool | MarkerRoles | None,
                        marker_hidden: Optional[bool]) -> Optional[MarkerRoles]:
    """The roles of a break's marker, ``None`` for no marker (#116 §4.4)."""
    m = cfg.marker if marker is None else marker
    if m is False:
        return None
    if isinstance(m, MarkerRoles):
        return m
    hidden = cfg.marker_hidden if marker_hidden is None else marker_hidden
    return MarkerRoles(stop=True, listed=not hidden)


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


# ---------------------------------------------------------------------------
# st_slide — one slide inside a block: its break, then its container (#81)
# ---------------------------------------------------------------------------

from contextlib import contextmanager as _contextmanager  # noqa: E402

from .styles import Style as _Style  # noqa: E402

#: The default box of a slide: at least 80 vh tall, 10 vh margins, content
#: centred vertically — the container both large projects wrap their slides
#: in (all-trainings ``slide_center``, sumvadis ``page_fill_top``).
SLIDE_CONTAINER = _Style(
    "min-height: 80vh; margin: 10vh 0; display: flex; flex-direction: column; "
    "justify-content: center;",
    "stx_slide",
)

_slide_container: Optional[_Style] = None
_CONTAINER_KEY = "_stx_slide_container"


def set_slide_container(style: Optional[_Style]) -> None:
    """Set the box every :func:`st_slide` uses (``None`` = ``SLIDE_CONTAINER``).

    One line in ``book.py``, before ``st_book``, with the design system's box::

        stx.set_slide_container(DS.containers.slide_center)

    Stored per session (#122): ``book.py`` runs at every rerun of every
    session, so each session gets its module's box, and two modules served
    by one process do not overwrite each other. Outside a session (tests,
    the ``stx`` CLIs) a process-wide fallback is used. The marker and TOC
    registries, the spacing state and the export buffer stay process-wide.
    """
    global _slide_container
    if _in_session():
        if style is None:
            st.session_state.pop(_CONTAINER_KEY, None)
        else:
            st.session_state[_CONTAINER_KEY] = style
    else:
        _slide_container = style


def get_slide_container() -> _Style:
    if _in_session():
        style = st.session_state.get(_CONTAINER_KEY)
        if style is not None:
            return style
    return _slide_container if _slide_container is not None else SLIDE_CONTAINER


#: The look of a text note (:func:`set_slide_note`): a small grey line, centred.
SLIDE_NOTE_STYLE = _Style("font-size: 0.75rem; color: #888; text-align: center; line-height: 1.3;",
                          "stx_slide_note")


@dataclass(frozen=True)
class _TextNote:
    text: object                      # a text, or a leaf {"en": …, "fr": …}
    link: Optional[str]
    style: _Style


_slide_note = None
_NOTE_KEY = "_stx_slide_note"


def set_slide_note(note=None, *, link: Optional[str] = None, style: Optional[_Style] = None) -> None:
    """Set the note drawn at the foot of every :func:`st_slide` (``None`` = no note).

    One line in ``book.py``, before ``st_book`` (board ``note1``)::

        stx.set_slide_note({"fr": "© 2026 … — lecture réservée aux participants",
                            "en": "© 2026 … — for the participants only"}, link="legal-notice")

    *note* is a text or a leaf ``{"en": …, "fr": …}`` (the module's language
    is used), drawn as one small line, a link to the marker *link* if given
    (it opens in a new tab: the reader keeps the slide) — or a function
    drawing the note itself, called after every slide. A text note sits in
    the bottom margin of the slide box and adds no height; with
    ``box=False``, and for a function, the note follows the content.
    :func:`st_slide_note` draws it on a page without ``st_slide``.

    Stored per session, as :func:`set_slide_container` (#122): two modules
    served by one process do not share their note.
    """
    global _slide_note
    if callable(note):
        if link is not None or style is not None:
            raise ValueError("set_slide_note: link= and style= go with a text; a function draws its own note")
    elif note is not None:
        if not isinstance(note, (str, dict)) or not note:
            raise TypeError("set_slide_note: a text, a leaf {'en': …, 'fr': …}, a function, or None")
        note = _TextNote(note, link, style if style is not None else SLIDE_NOTE_STYLE)
    elif link is not None or style is not None:
        raise ValueError("set_slide_note: link= and style= need a note")
    if _in_session():
        if note is None:
            st.session_state.pop(_NOTE_KEY, None)
        else:
            st.session_state[_NOTE_KEY] = note
    else:
        _slide_note = note


def get_slide_note():
    """The note set by :func:`set_slide_note` for this session (``None``: none)."""
    if _in_session():
        note = st.session_state.get(_NOTE_KEY)
        if note is not None:
            return note
    return _slide_note


def _note_html(note: _TextNote, foot: bool) -> str:
    import html

    from .deeplink import marker_href
    from .i18n import T
    text = html.escape(T(note.text))
    if note.link:
        text = (f'<a href="{html.escape(marker_href(note.link))}" target="_blank" rel="noopener" '
                f'style="color: inherit; text-decoration: none;">{text}</a>')
    line = f'<div class="stx-slide-note" style="{note.style}">{text}</div>'
    if not foot:
        return line
    # just under the box, in its bottom margin (10vh in SLIDE_CONTAINER): a wrapper of no height (p1)
    return ('<div class="stx-slide-note-foot" style="position: relative; height: 0; overflow: visible;">'
            f'<div style="position: absolute; left: 0; right: 0; bottom: 7vh;">{line}</div></div>')


def st_slide_note(*, _foot: bool = False) -> None:
    """Draw the note of :func:`set_slide_note` here — on a page without ``st_slide``; nothing if none."""
    note = get_slide_note()
    if note is None:
        return
    if isinstance(note, _TextNote):
        _render(_note_html(note, _foot))
    else:
        note()


def _slide_marker(marker, key, roles) -> tuple[str, Optional[MarkerRoles]] | None:
    """``(label, roles)`` of the slide's explicit marker, ``None`` if none (#122)."""
    if marker is False:
        if key is not None or roles is not None:
            raise ValueError("st_slide: marker=False places no marker; key= and roles= need one")
        return None
    if marker is None and key is None and roles is None:
        return None
    if isinstance(marker, MarkerRoles):
        if roles is not None:
            raise TypeError("st_slide: give the roles once (marker=MarkerRoles or roles=)")
        marker, roles = True, marker
    label = marker if isinstance(marker, str) else ""
    if roles is None:
        # a labelled marker is listed (st_marker("X")); an unlabelled one is the
        # break's usual stop, not listed
        roles = MarkerRoles.NAMED if label else MarkerRoles.HIDDEN
    return label, roles


@_contextmanager
def st_slide(cut: bool = False, style: Optional[_Style] = None, *,
             marker=None, key: Optional[str] = None, roles: Optional[MarkerRoles] = None,
             box: bool = True, zoom: Optional[int] = None,
             spacing: Optional[Spacing] = None, config: Optional[SlideBreakConfig] = None):
    """One slide of a block: a break before it if *cut*, its marker, then its box.

    It adds nothing else: the title, the zoom of the content, the alignment
    and every size stay written in the block, slide by slide::

        with st_slide():                          # the first slide of a block
            ...
        with st_slide(cut=True, marker="RAG"):    # a break, its listed marker, the slide
            ...
        with st_slide(cut=True, style=s.project.containers.slide_top):
            ...                                   # this slide only: top-aligned

    The three forms of a block are written with it: **S** (the default, each
    slide in the module's box), **B** (inside a composite: free content cut
    by breaks, ``with st_slide(cut=True, box=False):``) and **D** (a slide
    taller than the screen that scrolls: ``with st_slide(marker="X",
    box=False):``).

    :param cut: ``True`` = ``st_slide_break()`` before the slide.
    :param style: a ``Style`` added (``+``) to the box for this slide.
    :param marker: the slide's own marker — at most one per slide (#116
        roles): ``None`` (default) as before (with *cut*, the break places
        its usual marker; without, none); ``False`` no marker (the break
        still draws its rule and spacer); ``True`` a stop, not listed;
        ``"Label"`` a stop, listed, with that label. With *cut* it takes the
        place of the break's marker; without, it is placed before the box.
        An explicit marker is placed whatever the break mode or the sidebar.
    :param key: the marker's stable deep-link key (as ``st_marker(key=)``).
    :param roles: the marker's roles (as ``st_marker(roles=)``), e.g.
        ``MarkerRoles.HIDDEN`` or ``MarkerRoles(listed=False, toc_lvl="2")``.
    :param box: ``False`` = no box, the content flows (forms B and D).

    The note of :func:`set_slide_note`, if any, closes every slide.
    :param zoom, spacing, config: settings of the break (``cut=True`` only),
        as ``st_slide_break`` takes them.
    """
    from .container import st_block

    if not box and style is not None:
        raise ValueError("st_slide: style= is added to the slide box; with box=False there is none")
    if not cut and (zoom is not None or spacing is not None or config is not None):
        raise ValueError("st_slide: zoom=, spacing= and config= set the break before the slide; "
                         "they need cut=True (use st_zoom inside the slide)")
    explicit = _slide_marker(marker, key, roles)

    if cut:
        if marker is None and explicit is None and zoom is None and spacing is None and config is None:
            st_slide_break()        # a slide boundary itself (the 0.7.37 call)
        else:
            if explicit is not None:
                label, r = explicit
                brk_marker, force = r, True
            else:
                label, brk_marker, force = "", (False if marker is False else None), False
            st_slide_break(marker_label=label, config=config, spacing=spacing, zoom=zoom,
                           marker=brk_marker, _marker_key=key, _force_marker=force)
    else:
        marker_slide_boundary("slide")
        if explicit is not None:
            label, r = explicit
            st_marker(label, key=key, roles=r)
    if not box:
        yield
        st_slide_note()
        return
    container = get_slide_container()
    with st_block(container + style if style is not None else container):
        yield
    st_slide_note(_foot=True)
