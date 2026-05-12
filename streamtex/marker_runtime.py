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

The JavaScript goes through ``streamlit.components.v1.html(..., height=0)``
(0-pixel iframe).  This API is **officially deprecated in Streamlit 1.56**
with removal announced for after 2026-06-01, with ``st.iframe`` named as the
replacement.  **HOWEVER**, switching this specific call site to ``st.iframe``
(0.6.19 + 0.6.20 attempts) produced two distinct failure modes on the FC
presentation deck:

* 0.6.19 (``st.iframe`` + Python-side ``session_state`` guard): some grid
  markers on paginated navigation never received their ``.stx-grid`` class,
  because Streamlit's reconciliation removes the ``st.iframe`` element from
  the DOM on subsequent reruns when ``inject_marker_runtime()`` short-circuits,
  silently destroying the ``MutationObserver``.
* 0.6.20 (``st.iframe`` + no guard + disconnect-then-reinstall): catastrophic
  over-tagging — 47 ``.stx-grid`` classes applied (vs. the expected 3 for
  the visible slide) plus a Chrome freeze.  Root cause not fully understood
  as of 2026-05-12.

``components.v1.html`` (used here) was empirically verified to work on
0.6.18 in the same conditions: stable observer across reruns, correct count
of class applications, no freeze.  Streamlit treats it as a "custom
component" whose iframe is persistent across reruns, which keeps the
``MutationObserver`` alive.  ``st.iframe`` is a regular Streamlit element
and is reconciled differently.

The legacy alternative ``st.html("<script>…</script>",
unsafe_allow_javascript=True)`` does not execute JavaScript at all: verified
empirically on Streamlit 1.52 → 1.57, the proto field is forwarded by the
Python API but the frontend strips ``<script>`` tags and DOM event handlers
regardless.  See ``documentation/maintenance/components.v1_issue/`` for
the reproducer (``reproducer/app.py`` probes A–E).

**TODO before 2026-06-01**: find an ``st.iframe``-based (or other
non-deprecated) injection strategy that preserves the observer across
paginated navigation without over-tagging.  Investigation lives in
``documentation/maintenance/components.v1_issue/``.

The observer is therefore written to reach back into
``window.parent.document`` so it operates on the host DOM despite living
in an iframe.  Same pattern as :mod:`streamtex.marker` and
:mod:`streamtex.bib_preview` (note: those two modules use ``st.iframe`` and
work because they don't rely on a long-lived ``MutationObserver`` — they
re-emit their JS on every rerun).
"""
from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

logger = logging.getLogger(__name__)

_SESSION_KEY = "__stx_marker_runtime_injected__"

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
    """Inject the global stylesheet + observer script, once per session.

    Idempotent across reruns: the Streamlit ``session_state`` flag prevents
    re-emission within a session, and the JavaScript itself is guarded by
    ``window.parent.__stxMarkerObs``.

    Two separate Streamlit calls (see the module docstring for why
    ``components.v1.html`` is used despite being deprecated):

    * ``st.html("<style>…</style>")`` — inline CSS in the host page.
    * ``components.v1.html("<script>…</script>", height=0)`` — JS in a
      0-pixel iframe (a "custom component") that Streamlit treats as
      persistent across reruns, keeping the MutationObserver alive.
    """
    if st.session_state.get(_SESSION_KEY):
        return

    css = _read_asset(_CSS_PATH)
    js = _read_asset(_JS_PATH)
    if not css and not js:
        return

    if css:
        st.html(f"<style>{css}</style>")
    if js:
        components.html(f"<script>{js}</script>", height=0)
    st.session_state[_SESSION_KEY] = True
    logger.debug("marker_runtime: injected (css=%d bytes, js=%d bytes)", len(css), len(js))


def _reset_for_tests() -> None:
    """Clear the session flag — test helper, not part of the public API."""
    if _SESSION_KEY in st.session_state:
        del st.session_state[_SESSION_KEY]
