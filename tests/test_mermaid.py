"""Unit tests for streamtex.mermaid — Mermaid diagram rendering."""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import streamtex.export as export_mod
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.mermaid import st_mermaid

SAMPLE_CODE = "graph TD\n    A --> B"


@contextmanager
def _patched_mermaid(**overrides):
    """Patch sys.modules for streamlit-mermaid and mermaid-py."""
    mermaid_lib = overrides.pop("mermaid", MagicMock())
    modules = {
        "streamlit_mermaid": MagicMock(),
        "mermaid": mermaid_lib,
        "mermaid.graph": MagicMock(),
    }
    modules.update(overrides)
    with patch.dict("sys.modules", modules):
        yield modules


# ---------------------------------------------------------------------------
# Live rendering
# ---------------------------------------------------------------------------

class TestLiveRendering:
    """Tests for the live Streamlit component path."""

    @patch("streamtex.mermaid.st")
    def test_calls_streamlit_mermaid_component(self, mock_st):
        """The streamlit-mermaid component is called with the code."""
        mock_module = MagicMock()
        with patch.dict("sys.modules", {"streamlit_mermaid": mock_module}):
            st_mermaid(SAMPLE_CODE)
            mock_module.st_mermaid.assert_called_once_with(SAMPLE_CODE)

    @patch("streamtex.mermaid.st")
    def test_fallback_when_component_missing(self, mock_st):
        """When streamlit-mermaid is not installed, show warning + code."""
        with patch.dict("sys.modules", {"streamlit_mermaid": None}):
            st_mermaid(SAMPLE_CODE)
        mock_st.warning.assert_called_once()
        mock_st.code.assert_called_once_with(SAMPLE_CODE, language="mermaid")


# ---------------------------------------------------------------------------
# Export rendering
# ---------------------------------------------------------------------------

class TestExportRendering:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.mermaid.st")
    def test_noop_when_inactive(self, mock_st):
        """No export output when export is not active."""
        with _patched_mermaid():
            st_mermaid(SAMPLE_CODE)
        assert generate_export_html() is None

    @patch("streamtex.mermaid.st")
    def test_export_svg_when_active(self, mock_st):
        """When export is active and mermaid-py succeeds, SVG is appended."""
        reset_export_buffer(ExportConfig(enabled=True))
        mock_lib = MagicMock()
        mock_lib.Mermaid.return_value.svg_response.text = "<svg>mermaid diagram</svg>"
        with _patched_mermaid(mermaid=mock_lib):
            st_mermaid(SAMPLE_CODE)
        html = generate_export_html()
        assert "stx-mermaid" in html
        assert "<svg>mermaid diagram</svg>" in html

    @patch("streamtex.mermaid.st")
    def test_export_fallback_on_error(self, mock_st):
        """When mermaid-py fails, raw code is exported as <pre>."""
        reset_export_buffer(ExportConfig(enabled=True))
        mock_lib = MagicMock()
        mock_lib.Mermaid.side_effect = RuntimeError("render failed")
        with _patched_mermaid(mermaid=mock_lib):
            st_mermaid(SAMPLE_CODE)
        html = generate_export_html()
        assert "stx-mermaid" in html
        assert "<pre" in html
        assert "graph TD" in html

    @patch("streamtex.mermaid.st")
    def test_export_escapes_html(self, mock_st):
        """Fallback properly escapes HTML special characters."""
        reset_export_buffer(ExportConfig(enabled=True))
        malicious = 'graph TD\n    A["<script>alert(1)</script>"] --> B'
        mock_lib = MagicMock()
        mock_lib.Mermaid.side_effect = RuntimeError("fail")
        with _patched_mermaid(mermaid=mock_lib):
            st_mermaid(malicious)
        html = generate_export_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
