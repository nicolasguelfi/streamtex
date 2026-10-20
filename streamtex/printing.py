"""Usage notice and print rules of a document (#107).

``st_book(notice=..., printable=...)`` sets them for one module, in the live
app and in every HTML export of it (``stx export html``, the "Download as..."
panel, the automatic exports).

- ``notice``: one line (``"…"`` or ``{"en": …, "fr": …}``), shown under the
  version in the sidebar, and alone on the printed sheet when printing is off.
- ``printable``: ``True`` (default) everything allowed; ``False`` no printing
  of the app, no PDF in the panel, no printing of the HTML export;
  :class:`PrintConfig` sets each one.

Printing off injects a ``@media print`` rule: the sheet shows the notice and
nothing else. No script, nothing else changes on screen. It is a stated rule,
not a lock: a screenshot or an edited HTML file remains possible.
"""

from __future__ import annotations

import html as _html
from dataclasses import dataclass

PRINT_KEY = "_stx_print"


@dataclass(frozen=True)
class PrintConfig:
    """What a reader may print or download, for one module.

    :param app_print: The browser's File › Print on the live app.
    :param app_pdf: The PDF box of the app's "Download as..." panel.
    :param html_print: The browser's File › Print (and "Save as PDF") on the
        exported HTML.
    :param app_html: The HTML box of the app's "Download as..." panel; the
        panel disappears when neither HTML nor PDF is left.
    """

    app_print: bool = True
    app_pdf: bool = True
    html_print: bool = True
    app_html: bool = True


def resolve_printable(printable: bool | PrintConfig) -> PrintConfig:
    """``True`` → all allowed; ``False`` → no printing and no PDF, HTML download kept."""
    if isinstance(printable, PrintConfig):
        return printable
    if printable is True:
        return PrintConfig()
    if printable is False:
        return PrintConfig(app_print=False, app_pdf=False, html_print=False)
    raise TypeError(f"printable must be True, False or a PrintConfig — got {printable!r}")


def print_state(printable: bool | PrintConfig = True, notice=None,
                lang: str | None = None) -> dict:
    """The rules of one document, as stored in the session (plain data)."""
    cfg = resolve_printable(printable)
    text = ""
    if notice:
        from .i18n import T
        text = T(notice, lang)
    return {"notice": text, "app_print": cfg.app_print, "app_pdf": cfg.app_pdf,
            "html_print": cfg.html_print, "app_html": cfg.app_html}


def get_print_state(session_state=None) -> dict:
    """The rules set by ``st_book`` for this session; everything allowed if none."""
    if session_state is None:
        import streamlit as st
        session_state = st.session_state
    return session_state.get(PRINT_KEY) or print_state()


def _css_string(text: str) -> str:
    """*text* as a CSS string literal, safe inside a ``<style>`` element."""
    out = text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\A ").replace("<", "\\3C ")
    return f'"{out}"'


def print_block_css(notice: str = "") -> str:
    """The ``@media print`` rule that prints the notice instead of the page."""
    return (
        "\n@media print {\n"
        "  body > * { display: none !important; }\n"
        f"  body::before {{ content: {_css_string(notice)}; display: block !important;"
        " margin: 30mm 20mm; font: 14pt/1.4 sans-serif; color: #000;"
        " text-align: center; white-space: pre-wrap; }\n"
        "}\n"
    )


def notice_html(notice: str, style: str = "") -> str:
    """The notice line of a sidebar (escaped), or ``""`` without a notice."""
    if not notice:
        return ""
    return f'<div class="stx-notice" style="{style}">{_html.escape(notice)}</div>'


def apply_html_print_rule(html: str, state: dict) -> str:
    """Add the print rule to an exported HTML file when ``html_print`` is off.

    Only the files a reader gets: the PDF pipeline never calls it.
    """
    if not html or state.get("html_print", True):
        return html
    css = print_block_css(state.get("notice", ""))
    if "</style>" in html:
        return html.replace("</style>", css + "</style>", 1)
    if "</head>" in html:
        return html.replace("</head>", f"<style>{css}</style></head>", 1)
    return f"<style>{css}</style>{html}"
