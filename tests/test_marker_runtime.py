"""Unit tests for streamtex.marker_runtime — Phase 0 scaffold.

Validates that:
  - the env-flag gating works (legacy :has() path is the default);
  - inject_marker_runtime() is idempotent within a session;
  - the global stylesheet and JS observer assets ship inside the package
    and contain the expected anchors (so subsequent phases can rely on them).
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest
import streamlit as st

from streamtex import marker_runtime
from streamtex.marker_runtime import (
    _CSS_PATH,
    _JS_PATH,
    _SESSION_KEY,
    inject_marker_runtime,
    is_marker_runtime_enabled,
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
# is_marker_runtime_enabled
# ---------------------------------------------------------------------------

class TestIsMarkerRuntimeEnabled:
    def test_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STX_USE_MARKER_RUNTIME", None)
            os.environ.pop("STX_USE_LEGACY_HAS", None)
            assert is_marker_runtime_enabled() is False

    def test_enabled_by_flag(self):
        with patch.dict(os.environ, {"STX_USE_MARKER_RUNTIME": "1"}, clear=False):
            os.environ.pop("STX_USE_LEGACY_HAS", None)
            assert is_marker_runtime_enabled() is True

    def test_legacy_override_wins(self):
        with patch.dict(os.environ, {
            "STX_USE_MARKER_RUNTIME": "1",
            "STX_USE_LEGACY_HAS": "1",
        }, clear=False):
            assert is_marker_runtime_enabled() is False


# ---------------------------------------------------------------------------
# inject_marker_runtime
# ---------------------------------------------------------------------------

class TestInjectMarkerRuntime:
    def test_noop_when_disabled(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("STX_USE_MARKER_RUNTIME", None)
            with patch("streamtex.marker_runtime.st.html") as mock_html:
                inject_marker_runtime()
                mock_html.assert_not_called()
            assert _SESSION_KEY not in st.session_state

    def test_injects_once_when_enabled(self):
        with patch.dict(os.environ, {"STX_USE_MARKER_RUNTIME": "1"}, clear=False):
            with patch("streamtex.marker_runtime.st.html") as mock_html:
                inject_marker_runtime()
                inject_marker_runtime()  # second call same session
                assert mock_html.call_count == 1
            assert st.session_state.get(_SESSION_KEY) is True

    def test_emits_style_and_script_tags(self):
        with patch.dict(os.environ, {"STX_USE_MARKER_RUNTIME": "1"}, clear=False):
            captured = {}

            def _capture(html: str) -> None:
                captured["html"] = html

            with patch("streamtex.marker_runtime.st.html", side_effect=_capture):
                inject_marker_runtime()
            assert "<style>" in captured["html"]
            assert "<script>" in captured["html"]
            # Observer asset signature.
            assert "__stxMarkerObs" in captured["html"]
            # Phase-0 CSS includes the universal marker-cell rule.
            assert "stx-marker-cell" in captured["html"]


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
        # Look for the kind-prefix concatenation pattern.
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
        assert callable(marker_runtime.is_marker_runtime_enabled)
