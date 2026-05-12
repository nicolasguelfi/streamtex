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
(0-pixel iframe).  ``components.v1.html`` is **officially deprecated in
Streamlit 1.56** (with ``st.html`` named as the replacement), but the
recommended replacement does not actually execute injected JavaScript:

* ``st.html("<script>…</script>", unsafe_allow_javascript=True)`` — script
  stripped by DOMPurify, ``window.*`` flags never set.
* ``st.html('<svg onload=…/>', unsafe_allow_javascript=True)`` — handler
  not fired.
* ``st.html('<img onerror=…>', unsafe_allow_javascript=True)`` — handler
  not fired.

Verified on Streamlit 1.57.0 (2026-05-12); also affects 1.54 through 1.57.
The ``unsafe_allow_javascript`` Python parameter exists since 1.52 and is
forwarded on the proto, but the frontend does not honor it in any released
version.  See ``documentation/maintenance/components.v1_issue/`` for the
reproducer and the migration plan when (or if) the flag is honored upstream.

The observer is therefore written to reach back into
``window.parent.document`` so it operates on the host DOM despite living
in an iframe.  Same pattern as :mod:`streamtex.marker` and
:mod:`streamtex.bib_preview` (both pre-existing uses of
``components.v1.html`` in the codebase).
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
      0-pixel iframe that reaches back to ``window.parent.document``.
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
