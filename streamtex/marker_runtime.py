"""Marker-based scoping runtime — replacement for the historical `:has()` pattern.

This module owns:

* The global stylesheet (``streamtex/static/css/stx_global.css``) that defines
  every StreamTeX construct (``.stx-block``, ``.stx-grid``, ``.stx-list``,
  ``.stx-list-item``, ``.stx-zoom``, ``.stx-span``, ``.stx-md-big``).
* The JavaScript MutationObserver
  (``streamtex/static/js/stx_marker_observer.js``) that turns each StreamTeX
  sentinel ``<span class="stx-marker" data-stx-kind="…">`` into the
  appropriate class on the parent ``[data-testid="stVerticalBlock"]``.

``st_book`` calls :func:`inject_marker_runtime` once per session, which
injects both assets into the parent Streamlit document.

Injection strategy
------------------
The CSS goes through ``st.html`` (renders inline in the host page, no iframe).

The JavaScript goes through ``st.iframe(..., height=1)`` (1-pixel iframe,
added in Streamlit 1.56 — the officially announced replacement for the
removed-after-2026-06-01 ``streamlit.components.v1.html`` API).

The legacy alternative, ``st.html("<script>…</script>",
unsafe_allow_javascript=True)``, does not execute JavaScript: verified
empirically on Streamlit 1.52 → 1.57, the proto field is forwarded by the
Python API but the frontend strips ``<script>`` tags and DOM event handlers
regardless.  See ``documentation/maintenance/components.v1_issue/`` for
the reproducer (``reproducer/app.py`` probes A–E).

The observer is therefore written to reach back into
``window.parent.document`` so it operates on the host DOM despite living
in an iframe.  Same pattern as :mod:`streamtex.marker` and
:mod:`streamtex.bib_preview`.
"""
from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_CSS_PATH = _STATIC_DIR / "css" / "stx_global.css"
_JS_PATH = _STATIC_DIR / "js" / "stx_marker_observer.js"


def _read_asset(path: Path) -> str:
    """Read a static asset, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.debug("marker_runtime: failed to read %s: %s", path, exc)
        return ""


def inject_marker_runtime() -> None:
    """Inject the global stylesheet + observer script.

    Called once per rerun (no Python-side ``session_state`` guard).
    Streamlit reconciles the emitted ``st.html`` and ``st.iframe`` elements
    to the same DOM nodes across reruns (same call site, same payload),
    so the CSS ``<style>`` tag is updated in place and the observer
    ``<iframe>`` is preserved.  The JavaScript itself is idempotent at the
    DOM level via a disconnect-then-reinstall pattern on
    ``window.parent.__stxMarkerObsHandle`` — if the previous observer was
    garbage-collected for any reason (e.g. Streamlit forced a reload of
    the iframe), the script re-installs cleanly.

    The previous implementation gated injection at the Python side via
    ``session_state``, but that caused the iframe to be reconciled-out
    of the DOM on reruns where ``inject_marker_runtime()`` short-circuited,
    silently destroying the observer.  See
    ``documentation/maintenance/components.v1_issue/`` for the
    investigation that led to this pattern.

    Two separate Streamlit calls:

    * ``st.html("<style>…</style>")`` — inline CSS in the host page.
    * ``st.iframe("<script>…</script>", height=1)`` — JS in a 1-pixel
      iframe that reaches back to ``window.parent.document``.
    """
    css = _read_asset(_CSS_PATH)
    js = _read_asset(_JS_PATH)
    if not css and not js:
        return

    if css:
        st.html(f"<style>{css}</style>")
    if js:
        st.iframe(f"<script>{js}</script>", height=1)
    logger.debug("marker_runtime: injected (css=%d bytes, js=%d bytes)", len(css), len(js))
