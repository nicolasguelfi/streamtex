"""Unit tests for streamtex.markdown — Markdown rendering."""

from unittest.mock import MagicMock, patch

import pytest

import streamtex.export as export_mod
from streamtex.export import ExportConfig, generate_export_html, reset_export_buffer
from streamtex.markdown import st_markdown
from streamtex.styles import Style

# ---------------------------------------------------------------------------
# Live rendering
# ---------------------------------------------------------------------------

class TestLiveRendering:
    @patch("streamtex.markdown.st")
    def test_inline_renders_via_st_markdown(self, mock_st):
        """Inline content is rendered via st.markdown()."""
        st_markdown("# Hello World")
        mock_st.markdown.assert_called_once_with("# Hello World", unsafe_allow_html=True)

    @patch("streamtex.markdown.st")
    @patch("streamtex.markdown.resolve_content", return_value="# From File")
    def test_file_loads_and_renders(self, mock_resolve, mock_st):
        """file= parameter loads content and renders it."""
        st_markdown(file="docs/readme.md")
        mock_resolve.assert_called_once_with("", file="docs/readme.md", encoding="utf-8")
        mock_st.markdown.assert_called_once_with("# From File", unsafe_allow_html=True)

    @patch("streamtex.markdown.st")
    def test_with_style_wraps_in_block(self, mock_st):
        """When style is provided, content is wrapped in st_block."""
        my_style = Style("border: 1px solid red;")
        with patch("streamtex.markdown.st_block") as mock_block:
            mock_block.return_value.__enter__ = MagicMock()
            mock_block.return_value.__exit__ = MagicMock(return_value=False)
            st_markdown("# Styled", style=my_style)
            mock_block.assert_called_once_with(my_style)

    @patch("streamtex.markdown.st")
    def test_empty_content_returns_none(self, mock_st):
        """Empty content does not call st.markdown()."""
        st_markdown("")
        mock_st.markdown.assert_not_called()

    def test_both_content_and_file_raises(self):
        """Providing both content and file raises ValueError."""
        with pytest.raises(ValueError, match="not both"):
            st_markdown("inline", file="some/file.md")

    @patch("streamtex.markdown.st")
    def test_no_style_does_not_wrap_in_block(self, mock_st):
        """Without style, content is rendered directly (no st_block)."""
        with patch("streamtex.markdown.st_block") as mock_block:
            st_markdown("# Plain")
            mock_block.assert_not_called()


# ---------------------------------------------------------------------------
# Export rendering
# ---------------------------------------------------------------------------

class TestExportRendering:
    def setup_method(self):
        export_mod._buffer = None

    def teardown_method(self):
        export_mod._buffer = None

    @patch("streamtex.markdown.st")
    def test_noop_when_inactive(self, mock_st):
        """No export output when export is not active."""
        st_markdown("# Hello")
        assert generate_export_html() is None

    @patch("streamtex.markdown.st")
    def test_export_mode_appends_html(self, mock_st):
        """When export is active, HTML is appended to the buffer."""
        reset_export_buffer(ExportConfig(enabled=True))
        st_markdown("# Hello **World**")
        html = generate_export_html()
        assert html is not None
        # Should contain the content in some form (markdown lib or fallback div)
        assert "Hello" in html
        assert "World" in html

    @patch("streamtex.markdown.st")
    def test_export_fallback_without_markdown_lib(self, mock_st):
        """When python-markdown is not installed, fallback wraps in <div>."""
        reset_export_buffer(ExportConfig(enabled=True))
        with patch.dict("sys.modules", {"markdown": None}):
            st_markdown("# Fallback test")
        html = generate_export_html()
        assert "<div>" in html
        assert "Fallback test" in html
