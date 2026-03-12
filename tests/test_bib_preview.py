"""Tests for bib_preview — bibliography hover card scaffold injection."""

from unittest.mock import patch


class TestInjectBibPreviewScaffold:
    def test_injects_css_via_st_html(self, mock_streamlit):
        """CSS block is injected via st.html()."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.components.v1.html") as mock_comp_html:
            inject_bib_preview_scaffold()

        # st.html called for CSS
        mock_streamlit["html"].assert_called_once()
        css_output = mock_streamlit["html"].call_args[0][0]
        assert "<style>" in css_output
        assert "#stx-bib-card" in css_output

    def test_injects_js_via_components_html(self, mock_streamlit):
        """JS block is injected via components.html() with height=0."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.components.v1.html") as mock_comp_html:
            inject_bib_preview_scaffold()

        mock_comp_html.assert_called_once()
        call_args = mock_comp_html.call_args
        js_output = call_args[0][0]
        assert "<script>" in js_output
        assert "stx-bib-card" in js_output
        assert call_args[1]["height"] == 0

    def test_js_contains_icon_svgs(self, mock_streamlit):
        """JS output includes SVG icons for copy, check, and open."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.components.v1.html") as mock_comp_html:
            inject_bib_preview_scaffold()

        js_output = mock_comp_html.call_args[0][0]
        assert "ICON_COPY" in js_output
        assert "ICON_CHECK" in js_output
        assert "ICON_OPEN" in js_output

    def test_css_contains_cite_styles(self, mock_streamlit):
        """CSS includes styles for .stx-cite elements."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.components.v1.html"):
            inject_bib_preview_scaffold()

        css_output = mock_streamlit["html"].call_args[0][0]
        assert ".stx-cite" in css_output
        assert ".stx-bib-title" in css_output
        assert ".stx-bib-authors" in css_output
        assert ".stx-bib-actions" in css_output

    def test_js_includes_mutation_observer(self, mock_streamlit):
        """JS sets up MutationObserver for dynamic cite elements."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.components.v1.html") as mock_comp_html:
            inject_bib_preview_scaffold()

        js_output = mock_comp_html.call_args[0][0]
        assert "MutationObserver" in js_output
        assert "attachBibListeners" in js_output
