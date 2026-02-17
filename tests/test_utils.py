"""Tests for StreamTeX utility functions."""

import os
import pytest
import streamtex.utils as _utils

strip_html = _utils.strip_html
generate_key = _utils.generate_key
contain_link = _utils.contain_link

# Module-level double-underscore names (no class mangling)
is_url = getattr(_utils, '__is_url')
is_absolute_path = getattr(_utils, '__is_absolute_path')
is_relative_path = getattr(_utils, '__is_relative_path')
get_mime_type = getattr(_utils, '__get_mime_type')


class TestStripHtml:
    def test_removes_tags(self):
        assert strip_html("<b>hello</b>") == "hello"

    def test_removes_nested_tags(self):
        assert strip_html("<div><span>text</span></div>") == "text"

    def test_plain_text_unchanged(self):
        assert strip_html("hello world") == "hello world"

    def test_empty_string(self):
        assert strip_html("") == ""


class TestGenerateKey:
    def test_default_prefix(self):
        key = generate_key()
        assert key.startswith("block-")

    def test_custom_prefix(self):
        key = generate_key("test")
        assert key.startswith("test-")

    def test_unique_keys(self):
        keys = {generate_key() for _ in range(100)}
        assert len(keys) == 100


class TestContainLink:
    def test_no_link_returns_original(self):
        result = contain_link("<span>text</span>", "")
        assert result == "<span>text</span>"

    def test_external_link_wraps(self):
        result = contain_link("text", "https://example.com")
        assert 'href="https://example.com"' in result
        assert "text" in result

    def test_internal_link(self):
        result = contain_link("text", "#section1")
        assert 'href="#section1"' in result
        assert "streamtex-link" not in result  # No hover for internal links

    def test_hover_adds_class(self):
        result = contain_link("text", "https://example.com", hover=True)
        assert "streamtex-link" in result

    def test_no_hover_no_class(self):
        result = contain_link("text", "https://example.com", hover=False)
        assert "streamtex-link" not in result

    def test_no_link_decor(self):
        result = contain_link("text", "https://example.com", no_link_decor=True)
        assert "text-decoration: none" in result


class TestUrlDetection:
    def test_http_url(self):
        assert is_url("http://example.com") is True

    def test_https_url(self):
        assert is_url("https://example.com") is True

    def test_www_url(self):
        assert is_url("www.example.com") is True

    def test_not_url(self):
        assert is_url("images/photo.png") is False

    def test_relative_path(self):
        assert is_url("./file.txt") is False


class TestPathDetection:
    def test_absolute_path(self):
        assert is_absolute_path("/usr/local/file") is True

    def test_relative_path_dot(self):
        assert is_relative_path("./file.txt") is True

    def test_relative_path_dotdot(self):
        assert is_relative_path("../file.txt") is True

    def test_relative_path_slash(self):
        assert is_relative_path("/file.txt") is True


class TestMimeType:
    def test_png(self):
        assert get_mime_type("image.png") == "image/png"

    def test_jpg(self):
        assert get_mime_type("photo.jpg") == "image/jpeg"

    def test_jpeg(self):
        assert get_mime_type("photo.jpeg") == "image/jpeg"

    def test_gif(self):
        assert get_mime_type("anim.gif") == "image/gif"

    def test_unsupported(self):
        assert get_mime_type("file.bmp") is None
