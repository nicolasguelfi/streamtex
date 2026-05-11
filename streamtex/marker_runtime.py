"""Marker-based scoping runtime — replacement for the legacy `:has()` pattern.

This module owns:

* The global stylesheet (``streamtex/static/css/stx_global.css``) that defines
  every StreamTeX construct (``.stx-block``, ``.stx-grid``, ``.stx-list``,
  ``.stx-list-item``, ``.stx-zoom``, ``.stx-span``, ``.stx-md-big``).
* The JavaScript MutationObserver
  (``streamtex/static/js/stx_marker_observer.js``) that turns each StreamTeX
  sentinel ``<span class="stx-marker" data-stx-kind="…">`` into the
  appropriate class on the parent ``[data-testid="stVerticalBlock"]``.

When the env var ``STX_USE_MARKER_RUNTIME`` is set to ``"1"``, ``st_book``
calls :func:`inject_marker_runtime` once per session, which injects both
assets into the parent Streamlit document.  The actual migration of each
StreamTeX construct from the legacy ``:has()`` injection to the marker
pattern happens phase by phase in subsequent releases (see
``documentation/maintenance/freeze-has/fix-plan.md``).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

_SESSION_KEY = "__stx_marker_runtime_injected__"
_FLAG_ENV = "STX_USE_MARKER_RUNTIME"
_LEGACY_ENV = "STX_USE_LEGACY_HAS"

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_CSS_PATH = _STATIC_DIR / "css" / "stx_global.css"
_JS_PATH = _STATIC_DIR / "js" / "stx_marker_observer.js"


def is_marker_runtime_enabled() -> bool:
    """Return ``True`` when the marker runtime should be used.

    Resolution order (Phase 4 default-on; Phase 5 deletes this function):

    1. If ``STX_USE_LEGACY_HAS=1`` is set, return ``False`` (escape hatch
       for users who want to temporarily fall back to the legacy
       ``:has()`` emit pattern — kept for one patch release, removed in
       0.6.16).
    2. If ``STX_USE_MARKER_RUNTIME=0`` is set, return ``False`` (explicit
       opt-out — also removed in 0.6.16).
    3. Otherwise return ``True`` — the marker runtime is now the default.
    """
    if os.environ.get(_LEGACY_ENV, "0") == "1":
        return False
    return os.environ.get(_FLAG_ENV, "1") != "0"


def _read_asset(path: Path) -> str:
    """Read a static asset, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.debug("marker_runtime: failed to read %s: %s", path, exc)
        return ""


def inject_marker_runtime() -> None:
    """Inject the global stylesheet + observer script, once per session.

    No-op when the marker runtime is disabled (see
    :func:`is_marker_runtime_enabled`).  Idempotent across reruns: the
    Streamlit ``session_state`` flag prevents re-emission within a session,
    and the JavaScript itself is guarded by ``window.__stxMarkerObs``.
    """
    if not is_marker_runtime_enabled():
        return
    if st.session_state.get(_SESSION_KEY):
        return

    css = _read_asset(_CSS_PATH)
    js = _read_asset(_JS_PATH)
    if not css and not js:
        return

    fragments: list[str] = []
    if css:
        fragments.append(f"<style>{css}</style>")
    if js:
        fragments.append(f"<script>{js}</script>")
    st.html("".join(fragments))
    st.session_state[_SESSION_KEY] = True
    logger.debug("marker_runtime: injected (css=%d bytes, js=%d bytes)", len(css), len(js))


def _reset_for_tests() -> None:
    """Clear the session flag — test helper, not part of the public API."""
    if _SESSION_KEY in st.session_state:
        del st.session_state[_SESSION_KEY]
