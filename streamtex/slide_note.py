"""Slide notes: lines the document's designer places on every slide, the screen or the bar (board ``note3``).

One or several notes, declared once in ``book.py`` before ``st_book``::

    stx.set_slide_notes(
        stx.SlideNote(text={"slides": SHORT, "document": SHORT, "html": LONG, "phone": None},
                      place="bar-before-counter", link="legal-notice"),
        stx.SlideNote(text="© Right-On-Skill", place="across", opacity=0.08),    # a watermark
    )

Each note has

- a **place**:
  - in the slide, drawn with every ``st_slide`` (app and HTML): ``below`` (just under the box, in
    its bottom margin), ``above``, ``left``, ``right`` (vertical text, read from top to bottom),
    ``across`` (a watermark over the box);
  - fixed on the screen, drawn once (app and HTML): ``screen-top``, ``screen-bottom``,
    ``screen-left``, ``screen-right``;
  - in the presentation bar (the app only; the HTML has no bar): ``bar-after-title``,
    ``bar-title``, ``bar-before-counter``;
- a **text per display mode**: a text, a leaf ``{"en": …, "fr": …}``, or a dict of modes —
  ``slides`` (the app, paginated), ``document`` (the app, continuous), ``html`` (both HTML forms),
  ``phone`` (a screen under 600 px), ``default`` — whose values are texts, leaves, or ``None``
  (no note in that mode); a missing mode takes ``default``;
- an **opacity** and a **style**, with defaults by place;
- a **layer**: ``under`` (default) draws the note beneath the content, so that a text of the slide
  placed over it hides it (NG, board ``note3``); ``over`` draws it above. Under the content a
  link stays clickable through a transparent copy of the link above it.

A slide place assumes the box of ``SLIDE_CONTAINER`` (80vh high, 10vh margins): under a slide
taller than the screen, the note follows the box. Stored per session, as ``set_slide_container``
(#122): two modules served by one process keep their own notes.
"""

from __future__ import annotations

import html as _html
from dataclasses import dataclass
from typing import Optional

import streamlit as st

from .styles import Style

SLIDE_PLACES = ("below", "above", "left", "right", "across")
SCREEN_PLACES = ("screen-top", "screen-bottom", "screen-left", "screen-right")
BAR_PLACES = ("bar-after-title", "bar-title", "bar-before-counter")
PLACES = SLIDE_PLACES + SCREEN_PLACES + BAR_PLACES
MODES = ("slides", "document", "html", "phone", "default")
LAYERS = ("under", "over")

#: The look of ``set_slide_note`` (0.7.70): a small grey line, centred.
SLIDE_NOTE_STYLE = Style("font-size: 0.75rem; color: #888; text-align: center; line-height: 1.3;",
                         "stx_slide_note")

_LINE = "font-size: 0.75rem; color: #888; text-align: center; line-height: 1.3; white-space: nowrap;"
_VERTICAL = "font-size: 0.7rem; color: #888; line-height: 1.3; white-space: nowrap;"
#: The default look and opacity of each place.
_DEFAULTS = {
    "line": (Style(_LINE, "stx_note_line"), 0.7),
    "vertical": (Style(_VERTICAL, "stx_note_vertical"), 0.7),
    "across": (Style("font-size: 5vw; font-weight: 700; color: #888; white-space: nowrap;", "stx_note_across"),
               0.08),
    "bar": (Style("", "stx_note_bar"), 0.7),
}


def _kind(place: str) -> str:
    if place in BAR_PLACES:
        return "bar"
    if place == "across":
        return "across"
    if place.endswith("left") or place.endswith("right"):
        return "vertical"
    return "line"


@dataclass(frozen=True)
class SlideNote:
    """One note: its text (per mode), place, link, opacity, style and layer (see the module)."""

    text: object
    place: str = "below"
    link: Optional[str] = None
    opacity: Optional[float] = None
    style: Optional[Style] = None
    layer: str = "under"

    def __post_init__(self):
        if self.place not in PLACES:
            raise ValueError(f"SlideNote: place={self.place!r} — one of {', '.join(PLACES)}")
        if self.layer not in LAYERS:
            raise ValueError(f"SlideNote: layer={self.layer!r} — 'under' or 'over'")
        if self.opacity is not None and not 0 <= self.opacity <= 1:
            raise ValueError("SlideNote: opacity goes from 0 (invisible) to 1")
        if not isinstance(self.text, (str, dict)) or not self.text:
            raise TypeError("SlideNote: text is a text, a leaf {'en': …, 'fr': …} or a dict of modes")
        if _by_mode(self.text):
            unknown = set(self.text) - set(MODES)
            if unknown:
                raise ValueError(f"SlideNote: unknown mode(s) {sorted(unknown)} — {', '.join(MODES)}")

    def text_for(self, mode: str) -> Optional[str]:
        """The text shown in *mode* (``None``: no note there), in the module's language."""
        from .i18n import T
        value = self.text
        if _by_mode(value):
            value = value.get(mode, value.get("default"))
        return None if value is None else T(value)

    @property
    def look(self) -> tuple[Style, float]:
        style, opacity = _DEFAULTS[_kind(self.place)]
        return (self.style if self.style is not None else style,
                self.opacity if self.opacity is not None else opacity)


def _by_mode(text) -> bool:
    return isinstance(text, dict) and any(k in MODES for k in text)


# --- Per-session storage (as set_slide_container, #122) ---------------------------------------

_notes: tuple = ()
_NOTES_KEY = "_stx_slide_notes"


def _in_session() -> bool:
    from .slide import _in_session as in_session
    return in_session()


def set_slide_notes(*notes) -> None:
    """Set the notes of the module (none: no note). Each is a :class:`SlideNote`, or a function that
    draws a note itself after every slide (``set_slide_note(function)``, 0.7.70)."""
    global _notes
    for n in notes:
        if not isinstance(n, SlideNote) and not callable(n):
            raise TypeError("set_slide_notes: SlideNote(…) or a function")
    if _in_session():
        if notes:
            st.session_state[_NOTES_KEY] = tuple(notes)
        else:
            st.session_state.pop(_NOTES_KEY, None)
    else:
        _notes = tuple(notes)


def get_slide_notes() -> tuple:
    """The notes of this session (an empty tuple: none)."""
    if _in_session():
        notes = st.session_state.get(_NOTES_KEY)
        if notes is not None:
            return notes
    return _notes


# --- Rendering ------------------------------------------------------------------------------

def _app_mode() -> str:
    try:
        from .book import _STX_VIEW_MODE_KEY
        view = st.session_state.get(_STX_VIEW_MODE_KEY, "Paginated") if _in_session() else "Paginated"
    except Exception:  # noqa: BLE001
        view = "Paginated"
    return "document" if view == "Continuous" else "slides"


def _variants(note: SlideNote) -> str:
    """The note's text for the app, the HTML and a phone: one span each, CSS shows the right one."""
    from .deeplink import marker_href
    texts = {"app": note.text_for(_app_mode()), "html": note.text_for("html"), "phone": note.text_for("phone")}

    def one(text):
        if not text:
            return ""
        t = _html.escape(text)
        if note.link:
            t = (f'<a href="{_html.escape(marker_href(note.link))}" target="_blank" rel="noopener" '
                 f'style="color: inherit; text-decoration: none;">{t}</a>')
        return t

    if len(set(texts.values())) == 1:
        return one(texts["app"])
    return "".join(f'<span class="stx-sn-{k}">{one(v)}</span>' for k, v in texts.items())


#: Where a slide place sits, from a wrapper of no height just under the box's bottom margin.
_SLIDE_POS = {
    "below": "bottom: 7vh; left: 0; right: 0; text-align: center;",
    "above": "bottom: 91vh; left: 0; right: 0; text-align: center;",
    "left": "bottom: 10vh; height: 80vh; left: 0;",
    "right": "bottom: 10vh; height: 80vh; right: 0;",
    "across": "bottom: 10vh; height: 80vh; left: 0; right: 0;",
}
_SCREEN_POS = {
    "screen-top": "top: 0; left: 0; right: 0; text-align: center;",
    "screen-bottom": "bottom: var(--stx-sn-bottom, 0px); left: 0; right: 0; text-align: center;",
    "screen-left": "top: 0; bottom: 0; left: 0;",
    "screen-right": "top: 0; bottom: 0; right: 0;",
}
_FLEX = "display: flex; align-items: center; justify-content: center;"


def _inner(note: SlideNote) -> str:
    style, opacity = note.look
    kind = _kind(note.place)
    extra = ""
    if kind == "vertical":
        extra = " writing-mode: vertical-rl;"
    elif kind == "across":
        extra = " transform: rotate(-30deg);"
    return f'<div class="stx-slide-note" style="{style} opacity: {opacity};{extra}">{_variants(note)}</div>'


def _positioned(note: SlideNote, pos: str, fixed: bool) -> str:
    """The note at *pos*; under the content, its link gets a transparent copy above it."""
    box = "position: fixed;" if fixed else "position: absolute;"
    flex = _FLEX if _kind(note.place) in ("vertical", "across") else ""
    inner = _inner(note)
    if note.layer == "over":
        return f'<div class="stx-sn-over" style="{box} {pos} {flex}">{inner}</div>'
    out = f'<div class="stx-sn-under" style="{box} {pos} {flex}">{inner}</div>'
    if note.link:
        out += f'<div class="stx-sn-click" style="{box} {pos} {flex}">{inner}</div>'
    return out


def slide_notes_html(foot: bool) -> str:
    """The slide notes closing one slide: positioned around its box (*foot*), else as lines that follow
    the content (``box=False``, :func:`st_slide_note`)."""
    notes = [n for n in get_slide_notes() if isinstance(n, SlideNote) and n.place in SLIDE_PLACES]
    if not notes:
        return ""
    if not foot:
        return "".join(_inner(n) for n in notes)
    inside = "".join(_positioned(n, _SLIDE_POS[n.place], fixed=False) for n in notes)
    return ('<div class="stx-slide-note-foot" style="position: relative; height: 0; overflow: visible;">'
            f"{inside}</div>")


def draw_slide_notes(foot: bool) -> None:
    """Draw the notes closing a slide: the slide notes, then the functions of ``set_slide_note``."""
    from .export import st_html
    out = slide_notes_html(foot)
    if out:
        st_html(out)
    for n in get_slide_notes():
        if not isinstance(n, SlideNote):
            n()


def screen_notes_html() -> str:
    """The notes fixed on the screen (drawn once per page, not per slide)."""
    return "".join(_positioned(n, _SCREEN_POS[n.place], fixed=True) for n in get_slide_notes()
                   if isinstance(n, SlideNote) and n.place in SCREEN_PLACES)


def bar_notes_html(place: str) -> str:
    """The notes of one place of the presentation bar."""
    return "".join(_inner(n) for n in get_slide_notes() if isinstance(n, SlideNote) and n.place == place)


#: The rules of the notes. The app's root is isolated so that a note under the content stays above
#: the page's background; a transparent copy of a link stays clickable above the content.
_CSS = (".stx-sn-under { z-index: -1; pointer-events: none; }"
        ".stx-sn-over { z-index: 900; pointer-events: none; }"
        ".stx-sn-over a, .stx-sn-click a { pointer-events: auto; }"
        ".stx-sn-click { z-index: 900; pointer-events: none; }"
        ".stx-sn-click, .stx-sn-click * { color: transparent !important; }"
        ".stx-sn-html, .stx-sn-phone { display: none; }")
_PHONE = ("@media (max-width: 600px) { .stx-sn-app, .stx-sn-html { display: none !important; }"
          " .stx-sn-phone { display: inline !important; } }")
_APP_CSS = ".stApp { isolation: isolate; }" + _CSS + _PHONE
_EXPORT_CSS = ("body { isolation: isolate; }" + _CSS
               + ".stx-sn-app { display: none !important; } .stx-sn-html { display: inline !important; }" + _PHONE)


def st_slide_notes_page() -> None:
    """Once per page of the app, from ``st_book``: the rules and the notes fixed on the screen. They go
    to the screen only: the export adds its own (:func:`apply_slide_notes`), in every page file."""
    notes = get_slide_notes()
    if not any(isinstance(n, SlideNote) for n in notes):
        return
    css = _APP_CSS
    try:
        from .presentation import get_presentation_config
        cfg = get_presentation_config()
        if cfg is not None and cfg.footer:
            css += f":root {{ --stx-sn-bottom: {cfg.footer_height}; }}"
    except Exception:  # noqa: BLE001
        pass
    st.html(f"<style>{css}</style>{screen_notes_html()}")


def apply_slide_notes(html: str) -> str:
    """An exported HTML document with the notes' rules and the notes fixed on the screen, before
    ``</body>``: in the tail every page file of a paginated export shares."""
    if not html or not any(isinstance(n, SlideNote) for n in get_slide_notes()):
        return html
    block = f'<style>{_EXPORT_CSS}</style><div class="stx-sn-export">{screen_notes_html()}</div>'
    if "</body>" in html:
        i = html.rfind("</body>")
        return html[:i] + block + html[i:]
    return html + block
