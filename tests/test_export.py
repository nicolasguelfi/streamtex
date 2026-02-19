"""Unit tests for streamtex.export — buffer, config, global functions, _render."""

from unittest.mock import patch, MagicMock
import pytest

from streamtex.export import (
    ExportConfig,
    HtmlExportBuffer,
    reset_export_buffer,
    is_export_active,
    export_append,
    export_push_wrapper,
    export_pop_wrapper,
    generate_export_html,
    _render,
    st_export,
)
import streamtex.export as export_mod


# ---------------------------------------------------------------------------
# ExportConfig
# ---------------------------------------------------------------------------

class TestExportConfig:
    def test_defaults(self):
        cfg = ExportConfig()
        assert cfg.enabled is False
        assert cfg.page_title == "StreamTeX Export"
        assert cfg.page_width == "1224pt"
        assert cfg.page_padding == "36pt"

    def test_custom(self):
        cfg = ExportConfig(enabled=True, page_title="My Book", page_width="800px", page_padding="20px")
        assert cfg.enabled is True
        assert cfg.page_title == "My Book"


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
# _render — dual rendering
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
