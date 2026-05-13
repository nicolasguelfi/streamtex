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

The JavaScript goes through ``st.components.v2.component(..., isolate_styles=False)``
— Streamlit's V2 custom-component API (stable, no deprecation marker, added
in 1.56).  With ``isolate_styles=False`` the JS executes **inline in the host
page** (no iframe, no shadow DOM), giving the observer direct access to
``document`` without ``window.parent`` indirection.

History (why not the alternatives):

* ``streamlit.components.v1.html`` — the API streamtex used up to 0.6.18.
  Works, but **deprecated in Streamlit 1.56** with announced removal after
  2026-06-01.
* ``st.iframe`` — Streamlit's runtime warning points at this as the v1
  replacement.  Functionally identical to v1.html for one-shot JS injection
  but **breaks long-lived MutationObservers**: Streamlit's reconciliation
  removes/recreates the iframe on subsequent reruns, destroying the
  observer (verified empirically on the FC presentation deck; see
  ``documentation/maintenance/components.v1_issue/``).
* ``st.html(..., unsafe_allow_javascript=True)`` — documented as a JS
  execution path since 1.52 but the released frontend (1.52 → 1.57) strips
  ``<script>`` tags and DOM event handlers regardless of the flag (DOMPurify
  sanitisation not bypassed by the Python-side proto flag).
* ``st.components.v2.component(js=…, isolate_styles=False)`` — what we use
  now.  Verified to install the observer cleanly, process all markers on
  paginated navigation, and survive reruns without reconciliation issues.

The observer JS file (``static/js/stx_marker_observer.js``) is wrapped in a
V2 default export so the IIFE inside runs when the component mounts.
"""
from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

logger = logging.getLogger(__name__)

_SESSION_KEY = "__stx_marker_runtime_injected__"

_STATIC_DIR = Path(__file__).resolve().parent / "static"
_CSS_PATH = _STATIC_DIR / "css" / "stx_global.css"
_JS_PATH = _STATIC_DIR / "js" / "stx_marker_observer.js"
_SCROLL_SPY_JS_PATH = _STATIC_DIR / "js" / "stx_scroll_spy.js"

_COMPONENT_NAME = "stx_marker_observer"


def _read_asset(path: Path) -> str:
    """Read a static asset, returning an empty string on failure."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.debug("marker_runtime: failed to read %s: %s", path, exc)
        return ""


def _wrap_observer_for_v2(*js_bodies: str) -> str:
    """Wrap one or more streamtex IIFEs inside a V2 default-export function.

    The shipped scripts are auto-installing IIFEs (``(function(){…})();``).
    V2 expects a module-style ``export default function(ctx) { … }`` that
    Streamlit calls on mount.  We concatenate the IIFEs inside one
    function body so a single ``components.v2.component`` mount installs
    every runtime script in one shot — both the marker observer
    (``stx_marker_observer.js``) and the cross-context scroll-spy
    (``stx_scroll_spy.js``) ride together.  ``ctx`` is unused — the
    scripts reach the host DOM directly because ``isolate_styles=False``
    mounts inline (not in a shadow root).
    """
    body = "\n".join(b for b in js_bodies if b)
    return f"export default function(_ctx) {{\n{body}\n}}\n"


def inject_marker_runtime() -> None:
    """Inject the global stylesheet + observer script.

    The two assets live on different lifecycles:

    * **CSS** is re-emitted on every rerun via ``st.html``. Streamlit's
      reconciliation removes any element produced inside ``st_book`` if the
      corresponding call is absent on a subsequent rerun, so a one-shot
      ``st.html`` would silently disappear after the first user interaction.
      Re-emitting is cheap (the payload is identical, so the reconciler
      keeps the existing ``<style>`` element in place).

    * **JS observer + scroll-spy** is registered *once per session* via
      ``st.components.v2.component``. Re-registering on every rerun would
      log a ``Component … is already registered`` warning. The observer
      itself self-installs to ``window.__stxMarkerObsHandle`` and survives
      reconciliation of the component's host element, so single-shot
      registration is sufficient — every new DOM mutation across reruns
      is still picked up.

    The CSS path also guards against a DOMPurify quirk: the payload is
    handed to Streamlit's frontend, which runs it through DOMPurify, which
    rejects the entire ``st.html`` injection if it spots a literal
    ``<style>`` / ``</style>`` substring nested inside the outer style
    element (treats it as a forbidden nested style tag). The shipped
    ``stx_global.css`` references those tokens in documentation comments,
    so we break them with a single invisible whitespace before injection.
    """
    css = _read_asset(_CSS_PATH)
    js = _read_asset(_JS_PATH)
    scroll_spy_js = _read_asset(_SCROLL_SPY_JS_PATH)
    if not css and not js and not scroll_spy_js:
        return

    if css:
        # See docstring: defeat DOMPurify's nested-style-tag rejection.
        safe_css = css.replace("<style>", "< style>").replace("</style>", "</ style>")
        st.html(f"<style>{safe_css}</style>")

    # Component registration is gated to once per session to avoid
    # `is already registered` console warnings on every rerun.
    if not st.session_state.get(_SESSION_KEY):
        if js or scroll_spy_js:
            component = st.components.v2.component(
                _COMPONENT_NAME,
                js=_wrap_observer_for_v2(js, scroll_spy_js),
                isolate_styles=False,
            )
            component()
        st.session_state[_SESSION_KEY] = True
        logger.debug(
            "marker_runtime: registered (css=%d bytes, observer_js=%d bytes, scroll_spy_js=%d bytes)",
            len(css), len(js), len(scroll_spy_js),
        )


def _reset_for_tests() -> None:
    """Clear the session flag — test helper, not part of the public API."""
    if _SESSION_KEY in st.session_state:
        del st.session_state[_SESSION_KEY]
