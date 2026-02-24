"""Unit tests for streamtex.mermaid — Mermaid diagram rendering."""

from contextlib import contextmanager
from unittest.mock import MagicMock, patch

import streamtex.export as export_mod
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.mermaid import st_mermaid

SAMPLE_CODE = "graph TD\n    A --> B"


@contextmanager
def _patched_mermaid(**overrides):
    """Patch sys.modules for mermaid-py (export path only)."""
    mermaid_lib = overrides.pop("mermaid", MagicMock())
    modules = {
        "mermaid": mermaid_lib,
        "mermaid.graph": MagicMock(),
    }
    modules.update(overrides)
    with patch.dict("sys.modules", modules):
        yield modules


# ---------------------------------------------------------------------------
# Live rendering (via components.html with Mermaid JS CDN)
# ---------------------------------------------------------------------------

class TestLiveRendering:
    """Tests for the live components.html() rendering path."""

    @patch("streamtex.mermaid.components")
    def test_renders_via_components_html(self, mock_components):
        """The diagram is rendered via components.html()."""
        st_mermaid(SAMPLE_CODE)
        mock_components.html.assert_called_once()
        html_arg = mock_components.html.call_args[0][0]
        assert "mermaid" in html_arg
        assert "graph TD" in html_arg

    @patch("streamtex.mermaid.components")
    def test_light_bg_true_sets_white_background(self, mock_components):
        """When light_bg=True, background is white and theme is default."""
        st_mermaid(SAMPLE_CODE, light_bg=True)
        html_arg = mock_components.html.call_args[0][0]
        assert "#fff" in html_arg
        assert "'default'" in html_arg

    @patch("streamtex.mermaid.components")
    def test_light_bg_false_sets_transparent_background(self, mock_components):
        """When light_bg=False, background is transparent and theme is dark."""
        st_mermaid(SAMPLE_CODE, light_bg=False)
        html_arg = mock_components.html.call_args[0][0]
        assert "transparent" in html_arg
        assert "'dark'" in html_arg

    @patch("streamtex.mermaid.components")
    def test_default_height_500(self, mock_components):
        """Default height is 500 pixels."""
        st_mermaid(SAMPLE_CODE)
        assert mock_components.html.call_args[1]["height"] == 500

    @patch("streamtex.mermaid.components")
    def test_custom_height(self, mock_components):
        """Height parameter is forwarded to components.html()."""
        st_mermaid(SAMPLE_CODE, height=800)
        assert mock_components.html.call_args[1]["height"] == 800

    @patch("streamtex.mermaid.components")
    def test_scrolling_enabled(self, mock_components):
        """scrolling=True is passed to components.html() for interactivity."""
        st_mermaid(SAMPLE_CODE)
        assert mock_components.html.call_args[1]["scrolling"] is True

    @patch("streamtex.mermaid.components")
    def test_style_wraps_in_st_block(self, mock_components):
        """When style is provided, diagram is wrapped in st_block."""
        from streamtex.styles import Style
        my_style = Style("border: 1px solid red;")
        with patch("streamtex.mermaid.st_block") as mock_block:
            mock_block.return_value.__enter__ = MagicMock()
            mock_block.return_value.__exit__ = MagicMock(return_value=False)
            st_mermaid(SAMPLE_CODE, style=my_style)
            mock_block.assert_called_once_with(my_style)

    @patch("streamtex.mermaid.components")
    def test_escapes_html_in_code(self, mock_components):
        """HTML special characters in code are escaped."""
        malicious = 'graph TD\n    A["<script>alert(1)</script>"] --> B'
        st_mermaid(malicious)
        html_arg = mock_components.html.call_args[0][0]
        assert "<script>alert" not in html_arg
        assert "&lt;script&gt;" in html_arg

    @patch("streamtex.mermaid.components")
    def test_pan_zoom_js_included(self, mock_components):
        """The HTML includes pan-zoom JavaScript (wheel, mousedown)."""
        st_mermaid(SAMPLE_CODE)
        html_arg = mock_components.html.call_args[0][0]
        assert "addEventListener" in html_arg
        assert "wheel" in html_arg
        assert "mousedown" in html_arg
        assert "zoomIn" in html_arg
        assert "resetView" in html_arg

    @patch("streamtex.mermaid.components")
    def test_full_html_document(self, mock_components):
        """The HTML is a complete document (DOCTYPE, html, body)."""
        st_mermaid(SAMPLE_CODE)
        html_arg = mock_components.html.call_args[0][0]
        assert "<!DOCTYPE html>" in html_arg
        assert "<html>" in html_arg
        assert "<body>" in html_arg


# ---------------------------------------------------------------------------
# Fit parameter
# ---------------------------------------------------------------------------

class TestFitParameter:
    """Tests for the fit parameter (initial zoom mode)."""

    @patch("streamtex.mermaid.components")
    def test_default_fit_contain(self, mock_components):
        """Default fit='contain' injects contain auto-fit JS."""
        st_mermaid(SAMPLE_CODE)
        html_arg = mock_components.html.call_args[0][0]
        assert "var fitMode = 'contain'" in html_arg
        assert "Math.min(vpW / bb.width, vpH / bb.height)" in html_arg

    @patch("streamtex.mermaid.components")
    def test_fit_width(self, mock_components):
        """fit='width' injects width-only auto-fit JS."""
        st_mermaid(SAMPLE_CODE, fit="width")
        html_arg = mock_components.html.call_args[0][0]
        assert "var fitMode = 'width'" in html_arg

    @patch("streamtex.mermaid.components")
    def test_fit_none(self, mock_components):
        """fit='none' skips auto-fit (natural size)."""
        st_mermaid(SAMPLE_CODE, fit="none")
        html_arg = mock_components.html.call_args[0][0]
        assert "var fitMode = 'none'" in html_arg

    def test_fit_invalid_raises(self):
        """Invalid fit value raises ValueError."""
        import pytest
        with pytest.raises(ValueError, match="fit must be one of"):
            st_mermaid(SAMPLE_CODE, fit="invalid")

    @patch("streamtex.mermaid.components")
    def test_reset_restores_initial_fit(self, mock_components):
        """resetView() restores saved initial values, not hardcoded 1/0/0."""
        st_mermaid(SAMPLE_CODE)
        html_arg = mock_components.html.call_args[0][0]
        assert "_initS = _s; _initTx = _tx; _initTy = _ty" in html_arg
        assert "_s = _initS; _tx = _initTx; _ty = _initTy" in html_arg


# ---------------------------------------------------------------------------
# Export rendering
# ---------------------------------------------------------------------------

class TestExportRendering:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.mermaid.components")
    def test_noop_when_inactive(self, mock_components):
        """No export output when export is not active."""
        with _patched_mermaid():
            st_mermaid(SAMPLE_CODE)
        assert generate_export_html() is None

    @patch("streamtex.mermaid.components")
    def test_export_svg_when_active(self, mock_components):
        """When export is active and mermaid-py succeeds, SVG is appended."""
        reset_export_buffer(ExportConfig(enabled=True))
        mock_lib = MagicMock()
        mock_lib.Mermaid.return_value.svg_response.text = "<svg>mermaid diagram</svg>"
        with _patched_mermaid(mermaid=mock_lib):
            st_mermaid(SAMPLE_CODE)
        html = generate_export_html()
        assert "stx-mermaid" in html
        assert "<svg>mermaid diagram</svg>" in html

    @patch("streamtex.mermaid.components")
    def test_export_fallback_on_error(self, mock_components):
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

    @patch("streamtex.mermaid.components")
    def test_export_escapes_html(self, mock_components):
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
