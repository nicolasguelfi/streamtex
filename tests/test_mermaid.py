"""Unit tests for streamtex.mermaid — Mermaid diagram rendering."""

from unittest.mock import patch, MagicMock

import streamtex.export as export_mod
from streamtex.export import ExportConfig, reset_export_buffer, generate_export_html
from streamtex.mermaid import st_mermaid


SAMPLE_CODE = "graph TD\n    A --> B"


# ---------------------------------------------------------------------------
# Live rendering
# ---------------------------------------------------------------------------

class TestLiveRendering:
    """Tests for the live Streamlit component path."""

    @patch("streamtex.mermaid.st")
    @patch("streamtex.mermaid._component_mermaid", create=True)
    def test_calls_streamlit_mermaid_component(self, mock_component, mock_st):
        """The streamlit-mermaid component is called with the code."""
        with patch("streamtex.mermaid.st_mermaid.__module__", "streamtex.mermaid"):
            # We need to patch the import inside the function
            mock_module = MagicMock()
            mock_module.st_mermaid = MagicMock()
            with patch.dict("sys.modules", {"streamlit_mermaid": mock_module}):
                st_mermaid(SAMPLE_CODE)
                mock_module.st_mermaid.assert_called_once_with(SAMPLE_CODE)

    @patch("streamtex.mermaid.st")
    def test_fallback_when_component_missing(self, mock_st):
        """When streamlit-mermaid is not installed, show warning + code."""
        with patch.dict("sys.modules", {"streamlit_mermaid": None}):
            # Simulate ImportError by removing the module
            import sys
            saved = sys.modules.pop("streamlit_mermaid", None)
            try:
                # Force ImportError
                with patch("builtins.__import__", side_effect=_import_raiser("streamlit_mermaid")):
                    st_mermaid(SAMPLE_CODE)
                mock_st.warning.assert_called_once()
                mock_st.code.assert_called_once_with(SAMPLE_CODE, language="mermaid")
            finally:
                if saved is not None:
                    sys.modules["streamlit_mermaid"] = saved


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
        mock_module = MagicMock()
        with patch.dict("sys.modules", {"streamlit_mermaid": mock_module}):
            st_mermaid(SAMPLE_CODE)
        assert generate_export_html() is None

    @patch("streamtex.mermaid.st")
    def test_export_svg_when_active(self, mock_st):
        """When export is active and mermaid-py succeeds, SVG is appended."""
        reset_export_buffer(ExportConfig(enabled=True))

        mock_mermaid_component = MagicMock()
        mock_mermaid_lib = MagicMock()
        mock_graph_mod = MagicMock()

        # Build the mock Mermaid instance with svg_response
        mock_response = MagicMock()
        mock_response.text = "<svg>mermaid diagram</svg>"
        mock_mermaid_instance = MagicMock()
        mock_mermaid_instance.svg_response = mock_response
        mock_mermaid_lib.Mermaid.return_value = mock_mermaid_instance

        with patch.dict("sys.modules", {
            "streamlit_mermaid": mock_mermaid_component,
            "mermaid": mock_mermaid_lib,
            "mermaid.graph": mock_graph_mod,
        }):
            st_mermaid(SAMPLE_CODE)

        html = generate_export_html()
        assert "stx-mermaid" in html
        assert "<svg>mermaid diagram</svg>" in html

    @patch("streamtex.mermaid.st")
    def test_export_fallback_on_error(self, mock_st):
        """When mermaid-py fails, raw code is exported as <pre>."""
        reset_export_buffer(ExportConfig(enabled=True))

        mock_mermaid_component = MagicMock()
        mock_mermaid_lib = MagicMock()
        mock_mermaid_lib.Mermaid.side_effect = RuntimeError("render failed")
        mock_graph_mod = MagicMock()

        with patch.dict("sys.modules", {
            "streamlit_mermaid": mock_mermaid_component,
            "mermaid": mock_mermaid_lib,
            "mermaid.graph": mock_graph_mod,
        }):
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

        mock_mermaid_component = MagicMock()
        mock_mermaid_lib = MagicMock()
        mock_mermaid_lib.Mermaid.side_effect = RuntimeError("fail")
        mock_graph_mod = MagicMock()

        with patch.dict("sys.modules", {
            "streamlit_mermaid": mock_mermaid_component,
            "mermaid": mock_mermaid_lib,
            "mermaid.graph": mock_graph_mod,
        }):
            st_mermaid(malicious)

        html = generate_export_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _import_raiser(blocked_module):
    """Return an __import__ replacement that raises ImportError for *blocked_module*."""
    real_import = __builtins__.__import__ if hasattr(__builtins__, "__import__") else __import__

    def _fake_import(name, *args, **kwargs):
        if name == blocked_module:
            raise ImportError(f"No module named '{blocked_module}'")
        return real_import(name, *args, **kwargs)

    return _fake_import
