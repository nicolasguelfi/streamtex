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
        with patch("streamtex.marker_runtime.st.html") as mock_html:
            inject_marker_runtime()
            inject_marker_runtime()  # second call same session
            assert mock_html.call_count == 1
        assert st.session_state.get(_SESSION_KEY) is True

    def test_emits_style_and_script_tags(self):
        with patch("streamtex.marker_runtime.st.html") as mock_html:
            inject_marker_runtime()
        assert mock_html.call_count == 1
        args, kwargs = mock_html.call_args
        html_payload = args[0]
        assert "<style>" in html_payload
        assert "<script>" in html_payload
        # Observer asset signature.
        assert "__stxMarkerObs" in html_payload
        # Universal marker-cell rule lives in the global stylesheet.
        assert "stx-marker-cell" in html_payload

    def test_passes_unsafe_allow_javascript_flag(self):
        """Streamlit ≥ 1.54 strips <script> tags from st.html() unless
        unsafe_allow_javascript=True is explicitly set.  Without this flag
        the observer never runs and every marker-based rule silently
        no-ops (broken grids, no zoom, ignored font sizes, etc.)."""
        with patch("streamtex.marker_runtime.st.html") as mock_html:
            inject_marker_runtime()
        _, kwargs = mock_html.call_args
        assert kwargs.get("unsafe_allow_javascript") is True, (
            "inject_marker_runtime() must pass unsafe_allow_javascript=True "
            "to st.html() so the MutationObserver actually executes."
        )


# ---------------------------------------------------------------------------
# Static assets shipped in the package
# ---------------------------------------------------------------------------

class TestStaticAssets:
    def test_css_file_exists(self):
        assert _CSS_PATH.exists(), f"missing {_CSS_PATH}"

    def test_js_file_exists(self):
        assert _JS_PATH.exists(), f"missing {_JS_PATH}"

    def test_js_observer_has_idempotency_guard(self):
        js = _JS_PATH.read_text(encoding="utf-8")
        assert "window.__stxMarkerObs" in js, "observer must guard re-installation"

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
