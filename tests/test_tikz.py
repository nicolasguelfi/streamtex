"""Unit tests for streamtex.tikz — TikZ diagram rendering."""

from unittest.mock import MagicMock, patch

import streamtex.export as export_mod
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.tikz import _compile_tikz, _extract_svg_height, st_tikz

SAMPLE_CODE = r"""
\begin{tikzpicture}
  \draw (0,0) -- (1,1);
\end{tikzpicture}
"""

FAKE_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150"><line x1="0" y1="0" x2="1" y2="1"/></svg>'


# ---------------------------------------------------------------------------
# _compile_tikz pipeline
# ---------------------------------------------------------------------------

class TestCompileTikz:
    """Tests for the LaTeX compilation pipeline."""

    def setup_method(self):
        # Clear the st.cache_data cache between tests
        _compile_tikz.clear()

    @patch("streamtex.tikz.subprocess.run")
    @patch("builtins.open", create=True)
    @patch("streamtex.tikz.tempfile.TemporaryDirectory")
    def test_full_pipeline(self, mock_tmpdir, mock_file_open, mock_run):
        """The pipeline calls latex then dvisvgm and returns SVG."""
        # Set up temp directory
        mock_tmpdir.return_value.__enter__ = lambda s: "/tmp/stx_tikz_test"
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)

        # Mock file writes and reads
        mock_file_open.return_value.__enter__ = MagicMock()
        mock_file_open.return_value.__exit__ = MagicMock(return_value=False)

        # The last open() call reads the SVG
        file_handle = MagicMock()
        file_handle.read.return_value = FAKE_SVG
        mock_file_open.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=MagicMock(write=MagicMock())),
                      __exit__=MagicMock(return_value=False)),  # write .tex
            MagicMock(__enter__=MagicMock(return_value=file_handle),
                      __exit__=MagicMock(return_value=False)),  # read .svg
        ]

        # Both subprocess calls succeed
        mock_run.return_value = MagicMock(returncode=0)

        result = _compile_tikz(SAMPLE_CODE, "")
        assert "<svg" in result
        assert mock_run.call_count == 2

        # First call should be latex
        first_call_args = mock_run.call_args_list[0][0][0]
        assert first_call_args[0] == "latex"

        # Second call should be dvisvgm
        second_call_args = mock_run.call_args_list[1][0][0]
        assert second_call_args[0] == "dvisvgm"

    @patch("streamtex.tikz.subprocess.run", side_effect=FileNotFoundError("latex not found"))
    @patch("streamtex.tikz.tempfile.TemporaryDirectory")
    def test_raises_when_latex_missing(self, mock_tmpdir, mock_run):
        """FileNotFoundError is raised when latex is not installed."""
        mock_tmpdir.return_value.__enter__ = lambda s: "/tmp/stx_tikz_test"
        mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)

        # Mock the file write
        with patch("builtins.open", MagicMock()):
            try:
                _compile_tikz(SAMPLE_CODE + " unique1", "")
                assert False, "Should have raised FileNotFoundError"
            except FileNotFoundError:
                pass


# ---------------------------------------------------------------------------
# _extract_svg_height
# ---------------------------------------------------------------------------

class TestExtractSvgHeight:
    """Tests for SVG height extraction."""

    def test_extracts_integer_height(self):
        svg = '<svg width="200" height="150"><rect/></svg>'
        assert _extract_svg_height(svg) == 170  # 150 + 20 padding

    def test_extracts_float_height(self):
        svg = "<svg width='300.5' height='250.7'><rect/></svg>"
        assert _extract_svg_height(svg) == 270  # int(250.7) + 20

    def test_fallback_when_no_height(self):
        svg = "<svg><rect/></svg>"
        assert _extract_svg_height(svg) == 400


# ---------------------------------------------------------------------------
# st_tikz — live rendering
# ---------------------------------------------------------------------------

class TestLiveRendering:
    def setup_method(self):
        export_mod._buffer = None
        _compile_tikz.clear()

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.tikz._render")
    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", return_value=FAKE_SVG)
    def test_renders_svg_via_render(self, mock_compile, mock_st, mock_render):
        """Successful compilation displays SVG via _render() with height."""
        st_tikz(SAMPLE_CODE)
        mock_render.assert_called_once()
        call_arg = mock_render.call_args[0][0]
        assert "stx-tikz" in call_arg
        assert "<svg" in call_arg
        # height is extracted from the SVG (150px + 20px padding)
        assert mock_render.call_args[1]["height"] == 170

    @patch("streamtex.tikz.components")
    @patch("streamtex.tikz._render")
    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", return_value=FAKE_SVG)
    def test_explicit_height_uses_panzoom_template(
        self, mock_compile, mock_st, mock_render, mock_components
    ):
        """Explicit height renders via components.html with JS pan/zoom."""
        st_tikz(SAMPLE_CODE, height=800)
        mock_render.assert_not_called()
        mock_components.html.assert_called_once()
        html_arg = mock_components.html.call_args[0][0]
        # JS auto-fit pattern
        assert "Math.min(scaleX, scaleY)" in html_arg
        assert "resetView" in html_arg
        assert "_autoFit" in html_arg
        # Pan/zoom controls
        assert "zoomIn" in html_arg
        assert "zoomOut" in html_arg
        # SVG is injected
        assert "<svg" in html_arg
        # Correct height passed
        assert mock_components.html.call_args[1]["height"] == 800

    @patch("streamtex.tikz._render")
    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", side_effect=FileNotFoundError("not found"))
    def test_fallback_when_latex_missing(self, mock_compile, mock_st, mock_render):
        """When LaTeX is missing, show warning + raw code."""
        st_tikz(SAMPLE_CODE)
        mock_st.warning.assert_called_once()
        mock_st.code.assert_called_once_with(SAMPLE_CODE, language="latex")
        mock_render.assert_not_called()

    @patch("streamtex.tikz._render")
    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", side_effect=RuntimeError("compilation failed"))
    def test_fallback_on_compilation_error(self, mock_compile, mock_st, mock_render):
        """When compilation fails, show error + raw code."""
        st_tikz(SAMPLE_CODE)
        mock_st.error.assert_called_once()
        mock_st.code.assert_called_once_with(SAMPLE_CODE, language="latex")
        mock_render.assert_not_called()


# ---------------------------------------------------------------------------
# st_tikz — export rendering
# ---------------------------------------------------------------------------

class TestExportRendering:
    def setup_method(self):
        export_mod._buffer = None
        _compile_tikz.clear()

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", return_value=FAKE_SVG)
    def test_noop_when_inactive(self, mock_compile, mock_st):
        """No export output when export is not active."""
        st_tikz(SAMPLE_CODE)
        assert generate_export_html() is None

    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", return_value=FAKE_SVG)
    def test_export_svg_when_active(self, mock_compile, mock_st):
        """When export is active and compilation succeeds, SVG is appended."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_tikz(SAMPLE_CODE)
        html = generate_export_html()
        assert "stx-tikz" in html
        assert "<svg" in html

    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", side_effect=FileNotFoundError("not found"))
    def test_export_fallback_when_latex_missing(self, mock_compile, mock_st):
        """When LaTeX is absent, raw code is exported as <pre>."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_tikz(SAMPLE_CODE)
        html = generate_export_html()
        assert "stx-tikz" in html
        assert "<pre" in html
        assert "tikzpicture" in html

    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", side_effect=FileNotFoundError("not found"))
    def test_export_escapes_html(self, mock_st_mod, mock_compile):
        """Fallback properly escapes HTML special characters."""
        reset_export_buffer(ExportConfig(enabled=True))
        malicious = r'\begin{tikzpicture} <script>alert(1)</script> \end{tikzpicture}'
        st_tikz(malicious)
        html = generate_export_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html

    @patch("streamtex.tikz.st")
    @patch("streamtex.tikz._compile_tikz", return_value=FAKE_SVG)
    def test_preamble_forwarded(self, mock_compile, mock_st):
        """The preamble parameter is forwarded to _compile_tikz."""
        st_tikz(SAMPLE_CODE, preamble=r"\usepackage{pgfplots}")
        mock_compile.assert_called_once_with(SAMPLE_CODE, r"\usepackage{pgfplots}")
