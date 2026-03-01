"""Unit tests for streamtex.utils.resolve_content."""

from unittest.mock import patch

import pytest

from streamtex.utils import resolve_content


class TestResolveContent:
    """Tests for the resolve_content() utility."""

    def test_inline_content_returned_as_is(self):
        """Inline content string is returned unchanged."""
        assert resolve_content("hello world") == "hello world"

    def test_file_content_loaded(self, tmp_path):
        """File content is loaded when file= is provided."""
        f = tmp_path / "test.md"
        f.write_text("# Hello\nWorld", encoding="utf-8")
        with patch("streamtex.blocks.resolve_static", return_value=str(f)):
            result = resolve_content(file=str(f))
        assert result == "# Hello\nWorld"

    def test_both_raises_valueerror(self):
        """Providing both content and file raises ValueError."""
        with pytest.raises(ValueError, match="not both"):
            resolve_content("inline", file="some/file.md")

    def test_neither_returns_empty_string(self):
        """When neither content nor file is provided, returns empty string."""
        assert resolve_content() == ""

    def test_file_not_found_raises(self):
        """Non-existent file raises FileNotFoundError."""
        with patch("streamtex.blocks.resolve_static", return_value="/nonexistent/file.md"):
            with pytest.raises(FileNotFoundError):
                resolve_content(file="/nonexistent/file.md")

    def test_custom_encoding(self, tmp_path):
        """Custom encoding is used to read the file."""
        f = tmp_path / "latin1.txt"
        f.write_bytes("caf\xe9".encode("latin-1"))
        with patch("streamtex.blocks.resolve_static", return_value=str(f)):
            result = resolve_content(file=str(f), encoding="latin-1")
        assert result == "caf\xe9"

    def test_resolve_static_called(self, tmp_path):
        """resolve_static() is called with the file argument."""
        f = tmp_path / "diagram.mmd"
        f.write_text("graph TD\n    A --> B", encoding="utf-8")
        with patch("streamtex.blocks.resolve_static", return_value=str(f)) as mock_rs:
            resolve_content(file="diagrams/diagram.mmd")
        mock_rs.assert_called_once_with("diagrams/diagram.mmd")

    def test_empty_content_with_no_file_returns_empty(self):
        """Explicit empty string content returns empty string."""
        assert resolve_content(content="") == ""

    def test_content_with_file_none_returns_content(self):
        """Content with file=None returns the content string."""
        assert resolve_content("my content", file=None) == "my content"
