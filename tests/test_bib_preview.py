"""Tests for bib_preview — bibliography hover card scaffold injection."""

from unittest.mock import patch


class TestInjectBibPreviewScaffold:
    def test_injects_css_via_st_html(self, mock_streamlit):
        """CSS block is injected via st.html()."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.iframe"):
            inject_bib_preview_scaffold()

        mock_streamlit["html"].assert_called_once()
        css_output = mock_streamlit["html"].call_args[0][0]
        assert "<style>" in css_output
        assert "#stx-bib-card" in css_output

    def test_injects_js_via_st_iframe(self, mock_streamlit):
        """JS block is injected via st.iframe() with height=1."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.iframe") as mock_iframe:
            inject_bib_preview_scaffold()

        mock_iframe.assert_called_once()
        call_args = mock_iframe.call_args
        js_output = call_args[0][0]
        assert "<script>" in js_output
        assert "stx-bib-card" in js_output
        assert call_args[1]["height"] == 1

    def test_js_contains_icon_svgs(self, mock_streamlit):
        """JS output includes SVG icons for copy, check, and open."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.iframe") as mock_iframe:
            inject_bib_preview_scaffold()

        js_output = mock_iframe.call_args[0][0]
        assert "ICON_COPY" in js_output
        assert "ICON_CHECK" in js_output
        assert "ICON_OPEN" in js_output

    def test_css_contains_cite_styles(self, mock_streamlit):
        """CSS includes styles for .stx-cite elements."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.iframe"):
            inject_bib_preview_scaffold()

        css_output = mock_streamlit["html"].call_args[0][0]
        assert ".stx-cite" in css_output
        assert ".stx-bib-title" in css_output
        assert ".stx-bib-authors" in css_output
        assert ".stx-bib-actions" in css_output

    def test_js_includes_mutation_observer(self, mock_streamlit):
        """JS sets up MutationObserver for dynamic cite elements."""
        from streamtex.bib_preview import inject_bib_preview_scaffold

        with patch("streamlit.iframe") as mock_iframe:
            inject_bib_preview_scaffold()

        js_output = mock_iframe.call_args[0][0]
        assert "MutationObserver" in js_output
        assert "attachBibListeners" in js_output


class TestBibStyleOverrides:
    """BibConfig styling fields (cite_color / card_width / card_font_scale / card_css)."""

    def test_default_config_emits_only_base_css(self, mock_streamlit):
        """With default BibConfig, no override <style> is emitted (single st.html)."""
        from streamtex.bib import BibConfig, set_bib_config
        from streamtex.bib_preview import inject_bib_preview_scaffold

        set_bib_config(BibConfig())
        try:
            with patch("streamlit.iframe"):
                inject_bib_preview_scaffold()
            assert mock_streamlit["html"].call_count == 1
        finally:
            set_bib_config(BibConfig())

    def test_styling_fields_emit_override(self, mock_streamlit):
        """Styled BibConfig emits a second <style> with the configured rules."""
        from streamtex.bib import BibConfig, set_bib_config
        from streamtex.bib_preview import inject_bib_preview_scaffold

        set_bib_config(BibConfig(
            cite_color="#aab2c0",
            card_width="780px",
            card_font_scale=2.0,
            card_css="#stx-bib-card{max-height:70vh;overflow-y:auto;}",
        ))
        try:
            with patch("streamlit.iframe"):
                inject_bib_preview_scaffold()

            assert mock_streamlit["html"].call_count == 2
            override = mock_streamlit["html"].call_args_list[1][0][0]
            assert ".stx-cite{color:#aab2c0;}" in override
            assert "width:780px" in override
            # card_font_scale=2.0 -> title 14px*2 = 28px
            assert "font-size:28px" in override
            assert "max-height:70vh" in override  # raw card_css escape hatch
        finally:
            set_bib_config(BibConfig())
