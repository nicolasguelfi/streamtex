"""st_hover_tooltip — an inline icon that reveals a panel on CSS ``:hover``.

This is the canonical, **palette-neutral** hover tooltip. It lets a slide stay
light (keywords only) while detailed explanations live one hover away — the
"telegraphic slide + footnote-on-hover" technique. Projects or design packs
wrap this with their own palette (title/term/def colours, background) rather
than the library baking a theme in.

Why an HTML/CSS injection: vanilla Streamlit has no true CSS ``:hover`` panel
(``st.popover`` is click-based, ``help=`` only exists on widgets). The markup
is routed through StreamTeX's :func:`st_html` (not Streamlit's ``st.html``) so
it is captured by the HTML/PDF export buffer.

Placement guidance (matters for readability in projection):

- Open the panel on the side **opposite** the icon so it never spills off the
  slide. Icon at the right of a title → ``position="left"``; icon at the far
  bottom → ``direction="up"``.
- Keep panel content readable: a coloured title, short ``(term, definition)``
  bullets, a generous ``scale`` — not dense paragraphs.
"""

import hashlib

from .export import st_html

__all__ = ["st_hover_tooltip"]

# Neutral dark-theme defaults — override via *_style / bg_color for a palette.
_DEFAULT_SCALE = "1.8vw"
_DEFAULT_TITLE_COLOR = "#7AB8F5"
_DEFAULT_TERM_COLOR = "#7AB8F5"
_DEFAULT_DEF_COLOR = "#ccc"
_DEFAULT_BG = "rgba(17,17,17,0.94)"


def _font_style(scale: str, ratio: float, color: str, extra: str = "") -> str:
    """Build a CSS font declaration from a scale unit, ratio, and colour."""
    return f"font-size:calc({ratio} * {scale}); color:{color}; {extra}"


def _build_tooltip_html(
    icon: str = "ℹ️",
    title: str = "",
    entries: list[tuple[str, str]] | None = None,
    *,
    scale: str = _DEFAULT_SCALE,
    title_style: str | None = None,
    term_style: str | None = None,
    def_style: str | None = None,
    width: str = "40vw",
    height: str = "auto",
    max_height: str = "80vh",
    position: str = "center",
    direction: str = "down",
    bg_color: str = _DEFAULT_BG,
) -> str:
    """Build the tooltip's HTML/CSS string (pure — no rendering side effect)."""
    if title_style is None:
        title_style = _font_style(scale, 1.3, _DEFAULT_TITLE_COLOR, "font-weight:700;")
    if term_style is None:
        term_style = _font_style(scale, 1.1, _DEFAULT_TERM_COLOR, "font-weight:700;")
    if def_style is None:
        def_style = _font_style(scale, 1.0, _DEFAULT_DEF_COLOR, "line-height:1.45;")
    if entries is None:
        entries = []

    # Unique class so multiple tooltips on one page never share CSS.
    uid = hashlib.md5(
        f"{title}_{icon}_{len(entries)}".encode(), usedforsecurity=False
    ).hexdigest()[:8]
    cls = f"stx-tt-{uid}"

    # Horizontal placement: "left" anchors right (opens left), "right" anchors
    # left (opens right), "center" is symmetric.
    if position == "left":
        pos_h_css = "right: 0;"
    elif position == "center":
        pos_h_css = "left: 50%; transform: translateX(-50%);"
    else:
        pos_h_css = "left: 0;"

    pos_v_css = "bottom: 2.2rem;" if direction == "up" else "top: 2.2rem;"

    entries_html = ""
    for term, definition in entries:
        entries_html += (
            f'<div style="margin-bottom:0.5rem;">'
            f'<span style="{term_style}">{term}</span>'
            f'<span style="{def_style}"> &mdash; {definition}</span>'
            f"</div>"
        )

    html = f"""
    <style>
    .{cls} {{
        display: inline-block;
        position: relative;
        vertical-align: middle;
        margin-left: 0.4em;
        cursor: help;
    }}
    .{cls} .{cls}-icon {{
        font-size: 1.6rem;
        opacity: 0.7;
        transition: opacity 0.2s;
    }}
    .{cls}:hover .{cls}-icon {{ opacity: 1; }}
    .{cls} .{cls}-body {{
        display: none;
        position: absolute;
        {pos_v_css}
        {pos_h_css}
        z-index: 100;
        width: {width};
        height: {height};
        max-height: {max_height};
        overflow-y: auto;
        background: {bg_color};
        border: 1px solid rgba(122,184,245,0.3);
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        text-align: left;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        scrollbar-width: auto;
        scrollbar-color: rgba(122,184,245,0.4) rgba(255,255,255,0.05);
    }}
    .{cls} .{cls}-body::-webkit-scrollbar {{ width: 14px; }}
    .{cls} .{cls}-body::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.05);
    }}
    .{cls} .{cls}-body::-webkit-scrollbar-thumb {{
        background: rgba(122,184,245,0.4);
    }}
    .{cls} .{cls}-body::-webkit-scrollbar-thumb:hover {{
        background: rgba(122,184,245,0.6);
    }}
    .{cls}:hover .{cls}-body {{ display: block; }}
    </style>

    <span class="{cls}">
        <span class="{cls}-icon">{icon}</span>
        <div class="{cls}-body">
            <div style="{title_style} margin-bottom:0.6rem;">{icon} {title}</div>
            {entries_html}
        </div>
    </span>
    """
    return html


def st_hover_tooltip(
    icon: str = "ℹ️",
    title: str = "",
    entries: list[tuple[str, str]] | None = None,
    *,
    scale: str = _DEFAULT_SCALE,
    title_style: str | None = None,
    term_style: str | None = None,
    def_style: str | None = None,
    width: str = "40vw",
    height: str = "auto",
    max_height: str = "80vh",
    position: str = "center",
    direction: str = "down",
    bg_color: str = _DEFAULT_BG,
) -> None:
    """Render an inline icon that reveals a tooltip panel on hover.

    :param icon: Emoji or character displayed inline (e.g. ``"ℹ️"``, ``"💡"``).
    :param title: Tooltip panel title text.
    :param entries: List of ``(term, definition)`` tuples shown in the panel.
    :param scale: Base font unit (any CSS unit). Title is ``1.3×``, term
        ``1.1×``, definition ``1.0×`` of this. Larger ``scale`` = bigger,
        more legible tooltip text.
    :param title_style: CSS override for the panel title (wins over ``scale``).
    :param term_style: CSS override for each entry term (wins over ``scale``).
    :param def_style: CSS override for each definition (wins over ``scale``).
    :param width: CSS width of the panel (e.g. ``"40vw"``, ``"520px"``).
    :param height: CSS height of the panel (e.g. ``"auto"``, ``"30vh"``).
    :param max_height: CSS max-height — caps the panel and triggers an internal
        scrollbar when content exceeds (default ``"80vh"`` fits the viewport
        with margin). Pass ``"none"`` to disable the cap.
    :param position: Horizontal alignment — ``"left"`` (panel anchored right,
        opens toward the left), ``"center"``, or ``"right"`` (anchored left).
        Choose the side opposite the icon so the panel stays on-slide.
    :param direction: Vertical direction — ``"down"`` (opens below the icon) or
        ``"up"`` (opens above; use when the icon sits near the slide bottom).
    :param bg_color: CSS background colour of the panel.
    """
    st_html(_build_tooltip_html(
        icon, title, entries,
        scale=scale, title_style=title_style, term_style=term_style,
        def_style=def_style, width=width, height=height, max_height=max_height,
        position=position, direction=direction, bg_color=bg_color,
    ))
