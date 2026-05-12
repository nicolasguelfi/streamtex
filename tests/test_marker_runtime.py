"""Unit tests for streamtex.marker_runtime.

Validates that:
  - inject_marker_runtime() is idempotent within a session;
  - the global stylesheet and JS observer assets ship inside the package
    and contain the expected anchors.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import streamlit as st

from streamtex import marker_runtime
from streamtex.marker_runtime import (
    _CSS_PATH,
    _JS_PATH,
    _SESSION_KEY,
    inject_marker_runtime,
)


@pytest.fixture(autouse=True)
def _reset_marker_session():
    """Clear the session_state flag between tests."""
    if _SESSION_KEY in st.session_state:
        del st.session_state[_SESSION_KEY]
    yield
    if _SESSION_KEY in st.session_state:
        del st.session_state[_SESSION_KEY]


# ---------------------------------------------------------------------------
# inject_marker_runtime
# ---------------------------------------------------------------------------

class TestInjectMarkerRuntime:
    def test_injects_once_per_session(self):
        mock_v2 = MagicMock()
        with patch("streamtex.marker_runtime.st.html") as mock_html, \
             patch("streamtex.marker_runtime.st.components.v2.component",
                   return_value=mock_v2) as mock_v2_factory:
            inject_marker_runtime()
            inject_marker_runtime()  # second call same session
            assert mock_html.call_count == 1
            assert mock_v2_factory.call_count == 1
            assert mock_v2.call_count == 1
        assert st.session_state.get(_SESSION_KEY) is True

    def test_css_via_st_html(self):
        """CSS must go through st.html() — inline in the host page, no iframe."""
        with patch("streamtex.marker_runtime.st.html") as mock_html, \
             patch("streamtex.marker_runtime.st.components.v2.component"):
            inject_marker_runtime()
        assert mock_html.call_count == 1
        css_payload = mock_html.call_args[0][0]
        assert "<style>" in css_payload
        assert "stx-marker-cell" in css_payload  # universal marker-cell rule
        assert "<script>" not in css_payload     # no JS in this call

    def test_js_via_v2_component(self):
        """JS observer must go through st.components.v2.component with
        isolate_styles=False (inline DOM, no iframe).  This is the
        long-term replacement for streamlit.components.v1.html (removed
        2026-06-01).  See documentation/maintenance/components.v1_issue/
        for the investigation that ruled out st.iframe and
        st.html(unsafe_allow_javascript=True).
        """
        mock_v2 = MagicMock()
        with patch("streamtex.marker_runtime.st.html"), \
             patch("streamtex.marker_runtime.st.components.v2.component",
                   return_value=mock_v2) as mock_v2_factory:
            inject_marker_runtime()
        mock_v2_factory.assert_called_once()
        # First positional arg is the component name.
        args, kwargs = mock_v2_factory.call_args
        assert args[0] == "stx_marker_observer"
        # Inline (no shadow DOM, no iframe).
        assert kwargs.get("isolate_styles") is False
        # JS payload is wrapped in a V2 default export and contains the observer.
        js_payload = kwargs.get("js", "")
        assert "export default function" in js_payload
        assert "__stxMarkerObs" in js_payload
        # The wrapped component is then invoked once to mount it.
        mock_v2.assert_called_once()


# ---------------------------------------------------------------------------
# Static assets shipped in the package
# ---------------------------------------------------------------------------

class TestStaticAssets:
    def test_css_file_exists(self):
        assert _CSS_PATH.exists(), f"missing {_CSS_PATH}"

    def test_js_file_exists(self):
        assert _JS_PATH.exists(), f"missing {_JS_PATH}"

    def test_js_observer_has_idempotency_guard(self):
        """Observer must guard against running twice (the same script can be
        re-emitted on each Streamlit rerun); the guard lives on the
        parent window because the observer runs in an iframe."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "hostWin.__stxMarkerObs" in js, "observer must guard re-installation"

    def test_js_observer_uses_correct_parent_selector(self):
        js = _JS_PATH.read_text(encoding="utf-8")
        assert 'data-testid="stVerticalBlock"' in js

    def test_js_observer_handles_all_known_kinds(self):
        js = _JS_PATH.read_text(encoding="utf-8")
        for kind in ("block", "span", "grid", "list", "list-item", "zoom", "md-big"):
            assert f"'{kind}'" in js, f"missing kind {kind!r} in observer"

    def test_js_observer_uses_kind_prefixed_uid_attribute(self):
        """Observer must set `data-stx-{kind}-uid` on the parent, not a flat
        `data-stx-uid`, so multiple marker kinds (e.g. list-item wrapping
        st_block) can coexist without uid collision."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "'data-stx-' + kind + '-uid'" in js

    def test_js_observer_finds_element_container_both_naming(self):
        """Observer must find the marker's own cell on Streamlit ≤ 1.55
        (class `.element-container`) AND ≥ 1.56 (testid `stElementContainer`).
        Without this, marker cells stay visible and grab a grid slot — the
        exact bug seen on the FC presentation deck after the 1.56 upgrade."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert '[data-testid="stElementContainer"]' in js
        assert ".element-container" in js

    def test_js_observer_hides_marker_cell_inline(self):
        """Marker cell must be hidden via inline `display: none !important`
        (in addition to the class), so it stays hidden regardless of CSS
        cascade or stylesheet load order.  The write goes through the
        idempotent `setInlineImportant` helper."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "setInlineImportant(ec, 'display', 'none')" in js

    def test_js_observer_has_no_one_shot_processed_gate(self):
        """The observer must NOT use a one-shot `data-stx-processed` gate —
        Streamlit reconciliation can replace the parent stVerticalBlock on
        rerun (settings change, paginated navigation) while reusing the
        marker, so applyMarker must run again to re-apply the class +
        inline styles on the new parent."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "data-stx-processed" not in js

    def test_js_observer_watches_attribute_mutations(self):
        """The observer must watch attribute changes (not just childList) on
        the body subtree.  Streamlit's reconciliation can strip our class,
        uid, and inline style attributes on rerun without adding/removing
        any children — a childList-only observer misses that entirely and
        the user sees the layout collapse (sidebar slider regression)."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "attributes: true" in js
        assert "attributeFilter" in js
        # Filter must include the three families we care about.
        assert "'class'" in js
        assert "'style'" in js
        assert "'data-stx-block-uid'" in js
        assert "'data-stx-grid-uid'" in js

    def test_js_observer_uses_idempotent_inline_style_setter(self):
        """The attribute-watching observer would loop on itself if applyMarker
        re-wrote inline styles that were already set.  A `setInlineImportant`
        helper must skip the write when (value, priority) already match."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "setInlineImportant" in js
        # The helper must read getPropertyPriority to detect the !important
        # case correctly (otherwise the write looks needed even when it isn't).
        assert "getPropertyPriority" in js

    def test_js_observer_coalesces_via_animation_frame(self):
        """Many mutations during one Streamlit rerun must coalesce into a
        single batched handler on the next animation frame — otherwise
        the observer pegs the CPU during the cache-build mutation storm
        (the freeze reproduced by tests/e2e/test_cache_build_freeze.py).
        Since 0.6.26 the coalescing is via ``pendingBatch`` /
        ``pendingScheduled`` rather than the legacy ``pendingScan``."""
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "requestAnimationFrame" in js
        assert "pendingBatch" in js
        assert "pendingScheduled" in js

    def test_js_observer_clears_marker_state_on_removal(self):
        """When a marker span is detached from the DOM (e.g. Streamlit
        unmounts a slide during paginated navigation), the parent
        ``stVerticalBlock`` it was attached to may be reused by React
        for some other construct.  applyMarker only adds class / uid /
        inline styles — without a matching removal path, those persist
        and bleed into the next slide.  Reproduced empirically by
        tests/e2e/test_paginated_bleedthrough_fc.py before the fix.

        The fix introduces ``clearMarker`` which the batch handler runs
        on every removed marker, after additions, to leave the parent
        in the same shape it had before applyMarker ever touched it.
        """
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "function clearMarker(" in js
        # clearMarker must reverse every state change applyMarker writes
        # — guard each removal site so a future refactor doesn't silently
        # leave one of them out.
        assert "parent.classList.remove(cls)" in js
        assert "parent.removeAttribute(uidAttr)" in js
        assert "parent.style.removeProperty(props[j])" in js
        # And it must be wired into the mutation pipeline through
        # ``rec.removedNodes`` from childList records.
        assert "rec.removedNodes" in js

    def test_css_hides_marker_cells(self):
        css = _CSS_PATH.read_text(encoding="utf-8")
        assert ".stx-marker-cell" in css
        assert "display: none" in css


# ---------------------------------------------------------------------------
# Module surface
# ---------------------------------------------------------------------------

class TestModuleSurface:
    def test_public_symbols(self):
        assert callable(marker_runtime.inject_marker_runtime)
