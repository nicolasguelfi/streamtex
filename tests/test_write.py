"""Tests for st_write rendering."""

import pytest
from unittest.mock import patch, call
from streamtex.styles import Style, StxStyles
from streamtex.enums import Tags
from streamtex.write import st_write, _parse_args


class TestParseArgs:
    def test_style_as_first_arg(self):
        s = Style("color: red;", "red")
        container_style, txt = _parse_args(s, "hello")
        assert container_style is s
        assert txt == "hello"

    def test_no_style_uses_default(self):
        container_style, txt = _parse_args("hello")
        assert container_style is StxStyles.none
        assert txt == "hello"

    def test_tuple_style_text(self):
        s = Style("color: blue;", "blue")
        container_style, txt = _parse_args((s, "word"))
        assert '<span style="color: blue;">word</span>' in txt

    def test_tuple_style_text_link(self):
        s = Style("color: blue;", "blue")
        container_style, txt = _parse_args((s, "click", "https://example.com"))
        assert "https://example.com" in txt
        assert "click" in txt

    def test_mixed_args(self):
        s = Style("color: red;", "red")
        sub = Style("color: blue;", "blue")
        container_style, txt = _parse_args(s, "hello ", (sub, "world"))
        assert container_style is s
        assert "hello " in txt
        assert "world" in txt


class TestStWrite:
    def test_basic_write(self, mock_streamlit):
        st_write("Hello")
        mock_streamlit["html"].assert_called()
        html_output = mock_streamlit["html"].call_args[0][0]
        assert "Hello" in html_output

    def test_write_with_style(self, mock_streamlit):
        s = Style("color: red;", "red")
        st_write(s, "Styled text")
        html_output = mock_streamlit["html"].call_args[0][0]
        assert "color: red;" in html_output
        assert "Styled text" in html_output

    def test_write_with_tag(self, mock_streamlit):
        st_write("Title", tag=Tags.div)
        html_output = mock_streamlit["html"].call_args[0][0]
        assert "<div" in html_output
        assert "</div>" in html_output

    def test_write_with_link(self, mock_streamlit):
        st_write("Click me", link="https://example.com")
        html_output = mock_streamlit["html"].call_args[0][0]
        assert "https://example.com" in html_output
