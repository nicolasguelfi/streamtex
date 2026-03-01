"""Unit tests for streamtex.latex — LaTeX rendering (math + documents)."""

from unittest.mock import MagicMock, patch

import streamtex.export as export_mod
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.latex import st_latex, st_latex_doc

SAMPLE_MATH = r"E = mc^2"
SAMPLE_FRAGMENT = r"""
\section{Introduction}
This is a \textbf{bold} statement with math: $x^2 + y^2 = z^2$.
"""
SAMPLE_FULL_DOC = r"""
\documentclass{article}
\begin{document}
Hello from a full document.
\end{document}
"""


# ===========================================================================
# st_latex — Math formulas (Streamlit native)
# ===========================================================================

class TestStLatexLive:
    """Tests for the live st.latex() rendering path."""

    @patch("streamtex.latex.st")
    def test_calls_st_latex(self, mock_st):
        """st.latex() is called with the content."""
        st_latex(SAMPLE_MATH)
        mock_st.latex.assert_called_once_with(SAMPLE_MATH)

    @patch("streamtex.latex.st")
    def test_style_wraps_in_st_block(self, mock_st):
        """When style is provided, formula is wrapped in st_block."""
        from streamtex.styles import Style

        my_style = Style("border: 1px solid red;")
        with patch("streamtex.latex.st_block") as mock_block:
            mock_block.return_value.__enter__ = MagicMock()
            mock_block.return_value.__exit__ = MagicMock(return_value=False)
            st_latex(SAMPLE_MATH, style=my_style)
            mock_block.assert_called_once_with(my_style)

    @patch("streamtex.latex.st")
    def test_empty_content_is_noop(self, mock_st):
        """Empty content does not call st.latex()."""
        st_latex("")
        mock_st.latex.assert_not_called()

    @patch("streamtex.latex.st")
    @patch("streamtex.utils.resolve_content", return_value=SAMPLE_MATH)
    def test_file_parameter(self, mock_resolve, mock_st):
        """file= parameter loads content via resolve_content."""
        st_latex(file="formulas/euler.tex")
        mock_resolve.assert_called_once_with(
            "", file="formulas/euler.tex", encoding="utf-8"
        )
        mock_st.latex.assert_called_once_with(SAMPLE_MATH)


class TestStLatexExport:
    """Tests for the st_latex() export path."""

    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.latex.st")
    def test_noop_when_inactive(self, mock_st):
        """No export output when export is not active."""
        st_latex(SAMPLE_MATH)
        assert generate_export_html() is None

    @patch("streamtex.latex.st")
    def test_export_content(self, mock_st):
        """Export appends formula wrapped in stx-latex div."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_latex(SAMPLE_MATH)
        html = generate_export_html()
        assert "stx-latex" in html
        assert "E = mc^2" in html

    @patch("streamtex.latex.st")
    def test_export_escapes_html(self, mock_st):
        """HTML special characters are escaped in export."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_latex("<script>alert(1)</script>")
        html = generate_export_html()
        assert "<script>" not in html
        assert "&lt;script&gt;" in html


# ===========================================================================
# st_latex_doc — Full documents via LaTeX.js
# ===========================================================================

class TestStLatexDocLive:
    """Tests for the live components.html() rendering path."""

    @patch("streamtex.latex.components")
    def test_renders_via_components_html(self, mock_components):
        """The document is rendered via components.html() using programmatic API."""
        st_latex_doc(SAMPLE_FRAGMENT)
        mock_components.html.assert_called_once()
        html_arg = mock_components.html.call_args[0][0]
        assert "latex.mjs" in html_arg
        assert "HtmlGenerator" in html_arg
        assert "section" in html_arg

    @patch("streamtex.latex.components")
    def test_light_bg_true_sets_white(self, mock_components):
        """When light_bg=True, background is white."""
        st_latex_doc(SAMPLE_FRAGMENT, light_bg=True)
        html_arg = mock_components.html.call_args[0][0]
        assert "#fff" in html_arg

    @patch("streamtex.latex.components")
    def test_light_bg_false_sets_transparent(self, mock_components):
        """When light_bg=False, background is transparent."""
        st_latex_doc(SAMPLE_FRAGMENT, light_bg=False)
        html_arg = mock_components.html.call_args[0][0]
        assert "transparent" in html_arg

    @patch("streamtex.latex.components")
    def test_default_height_600(self, mock_components):
        """Default height is 600 pixels."""
        st_latex_doc(SAMPLE_FRAGMENT)
        assert mock_components.html.call_args[1]["height"] == 600

    @patch("streamtex.latex.components")
    def test_custom_height(self, mock_components):
        """Height parameter is forwarded to components.html()."""
        st_latex_doc(SAMPLE_FRAGMENT, height=400)
        assert mock_components.html.call_args[1]["height"] == 400

    @patch("streamtex.latex.components")
    def test_scrolling_enabled(self, mock_components):
        """scrolling=True is passed to components.html()."""
        st_latex_doc(SAMPLE_FRAGMENT)
        assert mock_components.html.call_args[1]["scrolling"] is True

    @patch("streamtex.latex.components")
    def test_style_wraps_in_st_block(self, mock_components):
        """When style is provided, iframe is wrapped in st_block."""
        from streamtex.styles import Style

        my_style = Style("border: 1px solid blue;")
        with patch("streamtex.latex.st_block") as mock_block:
            mock_block.return_value.__enter__ = MagicMock()
            mock_block.return_value.__exit__ = MagicMock(return_value=False)
            st_latex_doc(SAMPLE_FRAGMENT, style=my_style)
            mock_block.assert_called_once_with(my_style)

    @patch("streamtex.latex.components")
    def test_escapes_script_tags_in_code(self, mock_components):
        """</script> in LaTeX code cannot break out of the script tag."""
        malicious = r"\section{<script>alert(1)</script>}"
        st_latex_doc(malicious)
        html_arg = mock_components.html.call_args[0][0]
        # Only one real </script> closing tag (the template's own)
        assert html_arg.count("</script>") == 1
        # The malicious </script> is escaped as <\/script> inside the JS string
        assert "<\\/script>" in html_arg

    @patch("streamtex.latex.components")
    def test_fragment_wrapped_in_document(self, mock_components):
        """A fragment (no documentclass) is wrapped in a minimal article document."""
        st_latex_doc(SAMPLE_FRAGMENT)
        html_arg = mock_components.html.call_args[0][0]
        assert "latex.mjs" in html_arg
        # Fragment content should be present inside the JS string
        assert "section" in html_arg
        # The wrapper should be added for LaTeX.js to parse correctly
        assert "documentclass" in html_arg

    @patch("streamtex.latex.components")
    def test_full_doc_passed_as_is(self, mock_components):
        """A full document is passed as-is to LaTeX.js (not stripped)."""
        st_latex_doc(SAMPLE_FULL_DOC)
        html_arg = mock_components.html.call_args[0][0]
        # The body content should be present
        assert "Hello from a full document" in html_arg
        # The documentclass should be preserved for LaTeX.js
        assert "documentclass" in html_arg

    @patch("streamtex.latex.components")
    def test_hyphenate_true(self, mock_components):
        """Default hyphenation is enabled."""
        st_latex_doc(SAMPLE_FRAGMENT)
        html_arg = mock_components.html.call_args[0][0]
        assert "hyphenate: true" in html_arg

    @patch("streamtex.latex.components")
    def test_hyphenate_false(self, mock_components):
        """Hyphenation can be disabled."""
        st_latex_doc(SAMPLE_FRAGMENT, hyphenate=False)
        html_arg = mock_components.html.call_args[0][0]
        assert "hyphenate: false" in html_arg

    @patch("streamtex.latex.components")
    def test_complete_html_document(self, mock_components):
        """The HTML is a complete document (DOCTYPE, html, body)."""
        st_latex_doc(SAMPLE_FRAGMENT)
        html_arg = mock_components.html.call_args[0][0]
        assert "<!DOCTYPE html>" in html_arg
        assert "<html>" in html_arg
        assert "<body>" in html_arg

    @patch("streamtex.latex.components")
    def test_cdn_url_present(self, mock_components):
        """LaTeX.js CDN URL is injected in the HTML."""
        st_latex_doc(SAMPLE_FRAGMENT)
        html_arg = mock_components.html.call_args[0][0]
        assert "cdn.jsdelivr.net/npm/latex.js" in html_arg

    @patch("streamtex.latex.components")
    def test_empty_code_is_noop(self, mock_components):
        """Empty code does not call components.html()."""
        st_latex_doc("")
        mock_components.html.assert_not_called()


class TestStLatexDocExport:
    """Tests for the st_latex_doc() export path."""

    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.latex.components")
    def test_noop_when_inactive(self, mock_components):
        """No export output when export is not active."""
        st_latex_doc(SAMPLE_FRAGMENT)
        assert generate_export_html() is None

    @patch("streamtex.latex.components")
    def test_export_latex_js_embedded(self, mock_components):
        """Export includes latex-js web component with source."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_latex_doc(SAMPLE_FRAGMENT)
        html = generate_export_html()
        assert "stx-latex-doc" in html
        assert "latex-js" in html
        assert "section" in html

    @patch("streamtex.latex.components")
    def test_export_escapes_html(self, mock_components):
        """Export properly escapes HTML special characters."""
        reset_export_buffer(ExportConfig(enabled=True))
        malicious = r"\section{<script>alert(1)</script>}"
        st_latex_doc(malicious)
        html = generate_export_html()
        assert "<script>alert" not in html
        assert "&lt;script&gt;" in html


class TestStLatexDocFile:
    """Tests for the file= parameter."""

    @patch("streamtex.latex.components")
    @patch("streamtex.utils.resolve_content", return_value=SAMPLE_FRAGMENT)
    def test_file_loads_via_resolve_content(self, mock_resolve, mock_components):
        """file= parameter loads code via resolve_content."""
        st_latex_doc(file="docs/intro.tex")
        mock_resolve.assert_called_once_with(
            "", file="docs/intro.tex", encoding="utf-8"
        )
        html_arg = mock_components.html.call_args[0][0]
        assert "section" in html_arg
