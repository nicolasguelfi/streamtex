"""Unit tests for streamtex.export — buffer, config, global functions, st_html."""

from unittest.mock import patch

import streamtex.export as export_mod
from streamtex.export import (
    ExportConfig,
    HtmlExportBuffer,
    _render,
    export_append,
    export_pop_wrapper,
    export_push_wrapper,
    generate_export_html,
    is_export_active,
    reset_export_buffer,
    st_export,
    st_html,
)

# ---------------------------------------------------------------------------
# ExportConfig
# ---------------------------------------------------------------------------

class TestExportConfig:
    def test_defaults(self):
        cfg = ExportConfig()
        assert cfg.enabled is False
        assert cfg.page_title == "StreamTeX Export"
        assert cfg.page_width == "100%"
        assert cfg.page_padding == "var(--stx-page-padding, 36pt)"
        assert cfg.zoom == 1.0

    def test_custom(self):
        cfg = ExportConfig(enabled=True, page_title="My Book", page_width="800px", page_padding="20px")
        assert cfg.enabled is True
        assert cfg.page_title == "My Book"

    def test_custom_zoom(self):
        cfg = ExportConfig(enabled=True, zoom=0.8)
        assert cfg.zoom == 0.8


# ---------------------------------------------------------------------------
# HtmlExportBuffer
# ---------------------------------------------------------------------------

class TestHtmlExportBuffer:
    def _make_buffer(self):
        return HtmlExportBuffer(ExportConfig(enabled=True))

    def test_empty_buffer(self):
        buf = self._make_buffer()
        assert buf.get_body_html() == ""

    def test_append(self):
        buf = self._make_buffer()
        buf.append("<p>hello</p>")
        assert "<p>hello</p>" in buf.get_body_html()

    def test_multiple_appends(self):
        buf = self._make_buffer()
        buf.append("<p>a</p>")
        buf.append("<p>b</p>")
        body = buf.get_body_html()
        assert "<p>a</p>" in body
        assert "<p>b</p>" in body

    def test_push_pop_wrapper(self):
        buf = self._make_buffer()
        buf.push_wrapper('<div class="outer">')
        buf.append("<p>inner</p>")
        buf.pop_wrapper("</div>")
        body = buf.get_body_html()
        assert '<div class="outer">' in body
        assert "<p>inner</p>" in body
        assert "</div>" in body

    def test_nested_push_pop(self):
        buf = self._make_buffer()
        buf.push_wrapper("<div>")
        buf.push_wrapper("<section>")
        buf.append("<p>deep</p>")
        buf.pop_wrapper("</section>")
        buf.pop_wrapper("</div>")
        body = buf.get_body_html()
        assert "<div>" in body
        assert "<section>" in body
        assert "<p>deep</p>" in body
        assert "</section>" in body
        assert "</div>" in body

    def test_pop_on_root_is_safe(self):
        buf = self._make_buffer()
        buf.pop_wrapper("</div>")  # should not raise
        assert buf.get_body_html() == ""

    def test_reset(self):
        buf = self._make_buffer()
        buf.append("<p>data</p>")
        buf.reset()
        assert buf.get_body_html() == ""

    def test_generate_full_html(self):
        buf = self._make_buffer()
        buf.append("<p>content</p>")
        html = buf.generate_full_html()
        assert "<!DOCTYPE html>" in html
        assert "<title>StreamTeX Export</title>" in html
        assert "streamtex-page" in html
        assert "<p>content</p>" in html

    def test_generate_full_html_no_zoom_when_default(self):
        buf = self._make_buffer()
        buf.append("<p>test</p>")
        html = buf.generate_full_html()
        assert "zoom:" not in html

    def test_generate_full_html_with_zoom(self):
        buf = HtmlExportBuffer(ExportConfig(enabled=True, zoom=0.8))
        buf.append("<p>test</p>")
        html = buf.generate_full_html()
        assert "zoom: 0.8;" in html

    def test_generate_full_html_zoom_100_no_css(self):
        buf = HtmlExportBuffer(ExportConfig(enabled=True, zoom=1.0))
        buf.append("<p>test</p>")
        html = buf.generate_full_html()
        assert "zoom:" not in html


# ---------------------------------------------------------------------------
# Global functions
# ---------------------------------------------------------------------------

class TestGlobalFunctions:
    def setup_method(self):
        # Ensure clean state
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_inactive_by_default(self):
        assert is_export_active() is False

    def test_activate(self):
        reset_export_buffer(ExportConfig(enabled=True))
        assert is_export_active() is True

    def test_deactivate(self):
        reset_export_buffer(ExportConfig(enabled=True))
        reset_export_buffer(ExportConfig(enabled=False))
        assert is_export_active() is False

    def test_reset_none_config(self):
        reset_export_buffer(ExportConfig(enabled=True))
        reset_export_buffer(None)
        assert is_export_active() is False

    def test_noop_when_inactive(self):
        # These should not raise
        export_append("<p>x</p>")
        export_push_wrapper("<div>")
        export_pop_wrapper("</div>")
        assert generate_export_html() is None

    def test_export_append_when_active(self):
        reset_export_buffer(ExportConfig(enabled=True))
        export_append("<p>hello</p>")
        html = generate_export_html()
        assert "<p>hello</p>" in html

    def test_push_pop_when_active(self):
        reset_export_buffer(ExportConfig(enabled=True))
        export_push_wrapper("<div>")
        export_append("<p>inner</p>")
        export_pop_wrapper("</div>")
        html = generate_export_html()
        assert "<div>" in html
        assert "<p>inner</p>" in html
        assert "</div>" in html


# ---------------------------------------------------------------------------
# st_html — public dual-rendering bridge
# ---------------------------------------------------------------------------

class TestStHtml:
    """Tests for the public st_html() function."""

    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.export.st")
    def test_inline_calls_st_html(self, mock_st):
        st_html("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")

    @patch("streamtex.export.st")
    def test_appends_to_buffer(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        st_html("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")
        assert "<p>hi</p>" in generate_export_html()

    @patch("streamtex.export.st")
    def test_no_buffer_when_inactive(self, mock_st):
        st_html("<p>hi</p>")
        mock_st.html.assert_called_once()
        assert generate_export_html() is None

    def test_alias_is_same_function(self):
        assert _render is st_html

    @patch("streamlit.components.v1.html")
    def test_iframe_injects_font(self, mock_comp):
        st_html("<p>chart</p>", height=300)
        call_args = mock_comp.call_args
        html_arg = call_args[0][0]
        assert "font-family:Source Sans Pro,sans-serif" in html_arg
        assert "margin:0" in html_arg
        assert "<p>chart</p>" in html_arg

    @patch("streamlit.components.v1.html")
    def test_iframe_scrolling(self, mock_comp):
        st_html("<p>long</p>", height=400, scrolling=True)
        call_args = mock_comp.call_args
        assert call_args[1]["scrolling"] is True

    @patch("streamlit.components.v1.html")
    def test_iframe_no_scrolling_by_default(self, mock_comp):
        st_html("<p>short</p>", height=200)
        call_args = mock_comp.call_args
        assert call_args[1]["scrolling"] is False

    @patch("streamlit.components.v1.html")
    def test_iframe_buffer_gets_raw_html(self, mock_comp):
        """Export buffer receives the original HTML, not the iframe-wrapped version."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_html("<p>chart</p>", height=300)
        exported = generate_export_html()
        assert "<p>chart</p>" in exported
        # _IFRAME_BASE should NOT leak into export buffer
        assert "font-family:Source Sans Pro" not in exported


# ---------------------------------------------------------------------------
# _render — backward-compat alias (legacy tests kept for safety)
# ---------------------------------------------------------------------------

class TestRender:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.export.st")
    def test_render_calls_st_html(self, mock_st):
        _render("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")

    @patch("streamtex.export.st")
    def test_render_appends_to_buffer(self, mock_st):
        reset_export_buffer(ExportConfig(enabled=True))
        _render("<p>hi</p>")
        mock_st.html.assert_called_once_with("<p>hi</p>")
        assert "<p>hi</p>" in generate_export_html()

    @patch("streamtex.export.st")
    def test_render_no_buffer_when_inactive(self, mock_st):
        _render("<p>hi</p>")
        mock_st.html.assert_called_once()
        assert generate_export_html() is None


# ---------------------------------------------------------------------------
# st_export — context manager
# ---------------------------------------------------------------------------

class TestStExport:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    def test_noop_when_inactive(self):
        with st_export("<p>fallback</p>"):
            pass
        assert generate_export_html() is None

    def test_appends_when_active(self):
        reset_export_buffer(ExportConfig(enabled=True))
        with st_export("<p>fallback</p>"):
            pass
        html = generate_export_html()
        assert "<p>fallback</p>" in html

    def test_multiple_exports(self):
        reset_export_buffer(ExportConfig(enabled=True))
        with st_export("<p>first</p>"):
            pass
        with st_export("<p>second</p>"):
            pass
        html = generate_export_html()
        assert "<p>first</p>" in html
        assert "<p>second</p>" in html

    def test_yield_executes_body(self):
        reset_export_buffer(ExportConfig(enabled=True))
        executed = False
        with st_export("<p>fb</p>"):
            executed = True
        assert executed is True
