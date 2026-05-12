"""Unit tests for streamtex.marker_runtime.

Validates that:
  - inject_marker_runtime() is idempotent within a session;
  - the global stylesheet and JS observer assets ship inside the package
    and contain the expected anchors.
"""
from __future__ import annotations

from unittest.mock import patch

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
        with patch("streamtex.marker_runtime.st.html") as mock_html, \
             patch("streamtex.marker_runtime.st.iframe") as mock_iframe:
            inject_marker_runtime()
            inject_marker_runtime()  # second call same session
            assert mock_html.call_count == 1
            assert mock_iframe.call_count == 1
        assert st.session_state.get(_SESSION_KEY) is True

    def test_css_via_st_html(self):
        """CSS must go through st.html() — inline in the host page, no iframe."""
        with patch("streamtex.marker_runtime.st.html") as mock_html, \
             patch("streamtex.marker_runtime.st.iframe"):
            inject_marker_runtime()
        assert mock_html.call_count == 1
        css_payload = mock_html.call_args[0][0]
        assert "<style>" in css_payload
        assert "stx-marker-cell" in css_payload  # universal marker-cell rule
        assert "<script>" not in css_payload      # no JS in this call

    def test_js_via_st_iframe(self):
        """JS observer must go through st.iframe() — the
        components.v1.html replacement announced for removal after
        2026-06-01.  st.html(unsafe_allow_javascript=True) is documented
        as a JS-execution path but the released frontend (verified 1.52
        through 1.57) strips <script> tags and DOM event handlers
        regardless of the flag.  Only st.iframe (and the deprecated
        components.v1.html it replaces) actually execute injected JS.
        """
        with patch("streamtex.marker_runtime.st.html"), \
             patch("streamtex.marker_runtime.st.iframe") as mock_iframe:
            inject_marker_runtime()
        assert mock_iframe.call_count == 1
        args, kwargs = mock_iframe.call_args
        js_payload = args[0]
        assert "<script>" in js_payload
        # The observer reaches back to the host page via window.parent.
        assert "window.parent" in js_payload or "parent.document" in js_payload
        # Observer idempotency guard targets the parent window.
        assert "__stxMarkerObs" in js_payload
        # 1-pixel iframe (st.iframe rejects height=0 — minimum positive int).
        assert kwargs.get("height") == 1


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
