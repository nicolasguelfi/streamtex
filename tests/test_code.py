"""Tests for streamtex/code.py — syntax-highlighted code rendering."""

import sys
import pytest
from unittest.mock import patch, MagicMock


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _call_st_code(**kwargs):
    """Call st_code with _render mocked, return captured HTML string."""
    from streamtex.code import st_code
    captured = []
    with patch("streamtex.code._render", side_effect=captured.append):
        st_code(**kwargs)
    assert len(captured) == 1, "st_code should call _render exactly once"
    return captured[0]


# ---------------------------------------------------------------------------
# With Pygments available (default in test environment)
# ---------------------------------------------------------------------------

class TestStCodeWithPygments:
    def test_renders_html_output(self):
        html = _call_st_code(code="x = 1", language="python")
        assert "<div" in html
        assert "x = 1" in html or "x" in html  # Pygments may split tokens

    def test_line_numbers_table_included(self):
        html = _call_st_code(code="x = 1\ny = 2", language="python", line_numbers=True)
        # Pygments uses a <table> for linenos="table"
        assert "table" in html.lower() or "linenodiv" in html

    def test_line_numbers_false_no_table(self):
        html = _call_st_code(code="x = 1", language="python", line_numbers=False)
        # When line_numbers=False, the fmt_options don't set "linenos"
        # The line_no_css block is also absent
        assert "linenodiv" not in html

    def test_custom_font_size_appears_in_container(self):
        html = _call_st_code(code="pass", language="python", font_size="14pt")
        assert "14pt" in html

    def test_custom_line_number_color_in_css(self):
        html = _call_st_code(
            code="x = 1\ny = 2",
            language="python",
            line_numbers=True,
            line_number_color="#FF0000",
        )
        assert "#FF0000" in html

    def test_no_line_number_css_when_disabled(self):
        html = _call_st_code(
            code="x = 1",
            language="python",
            line_numbers=False,
            line_number_color="#FF0000",
        )
        # line_no_css block is only added when line_numbers=True
        assert "#FF0000" not in html

    def test_unknown_language_falls_back_to_text_lexer(self):
        # Should not raise; uses TextLexer fallback
        html = _call_st_code(code="some text", language="xyzunknown999")
        assert "some text" in html

    def test_container_div_wraps_output(self):
        html = _call_st_code(code="pass", language="python")
        # The outer container div is always present
        assert html.strip().endswith("</div>")

    def test_style_string_included_in_container(self):
        from streamtex.styles import Style
        s = Style("color: cyan;", "cyan_style")
        html = _call_st_code(style=s, code="pass", language="python")
        assert "color: cyan;" in html

    def test_default_monokai_colors_in_output(self):
        # Monokai background used in container style
        html = _call_st_code(code="x = 1", language="python")
        assert "#F8F8F2" in html  # monokai foreground color in container CSS

    def test_default_font_size_uses_css_variable(self):
        html = _call_st_code(code="pass", language="python")
        assert "--stx-code-size" in html
        assert "18pt" in html  # fallback value in var()

    def test_wrap_false_no_checked(self):
        html = _call_st_code(code="x = 1", language="python", wrap=False)
        # Checkbox should be present but NOT checked
        assert '<input type="checkbox"' in html
        assert "checked" not in html.split('<input type="checkbox"')[1].split("/>")[0]

    def test_wrap_true_has_pre_wrap_css(self):
        html = _call_st_code(code="x = 1", language="python", wrap=True)
        assert "white-space: pre-wrap" in html
        assert "word-break: break-word" in html
        assert "overflow-wrap: break-word" in html

    def test_wrap_default_none_falls_back_to_true(self):
        # wrap=None (default) falls back to True when no session state
        html = _call_st_code(code="x = 1", language="python")
        checkbox = html.split('<input type="checkbox"')[1].split("/>")[0]
        assert "checked" in checkbox

    def test_wrap_none_reads_session_state_false(self):
        """When session state has wrap_all=False, wrap=None uses it."""
        from streamtex.code import _WRAP_ALL_KEY
        mock_state = {_WRAP_ALL_KEY: False}
        with patch("streamtex.code.st") as mock_st:
            mock_st.session_state = mock_state
            html = _call_st_code(code="x = 1", language="python")
        checkbox = html.split('<input type="checkbox"')[1].split("/>")[0]
        assert "checked" not in checkbox

    def test_wrap_none_reads_session_state_true(self):
        """When session state has wrap_all=True, wrap=None uses it."""
        from streamtex.code import _WRAP_ALL_KEY
        mock_state = {_WRAP_ALL_KEY: True}
        with patch("streamtex.code.st") as mock_st:
            mock_st.session_state = mock_state
            html = _call_st_code(code="x = 1", language="python")
        checkbox = html.split('<input type="checkbox"')[1].split("/>")[0]
        assert "checked" in checkbox

    def test_wrap_explicit_overrides_session_state(self):
        """Explicit wrap=False wins over session state True."""
        from streamtex.code import _WRAP_ALL_KEY
        mock_state = {_WRAP_ALL_KEY: True}
        with patch("streamtex.code.st") as mock_st:
            mock_st.session_state = mock_state
            html = _call_st_code(code="x = 1", language="python", wrap=False)
        checkbox = html.split('<input type="checkbox"')[1].split("/>")[0]
        assert "checked" not in checkbox

    def test_toggle_checkbox_present(self):
        html = _call_st_code(code="x = 1", language="python")
        assert '<input type="checkbox"' in html

    def test_toggle_label_present(self):
        html = _call_st_code(code="x = 1", language="python")
        assert "<label for=" in html
        assert ">wrap</label>" in html

    def test_toggle_checked_when_wrap_true(self):
        html = _call_st_code(code="x = 1", language="python", wrap=True)
        checkbox = html.split('<input type="checkbox"')[1].split("/>")[0]
        assert "checked" in checkbox

    def test_toggle_unchecked_when_wrap_false(self):
        html = _call_st_code(code="x = 1", language="python", wrap=False)
        checkbox = html.split('<input type="checkbox"')[1].split("/>")[0]
        assert "checked" not in checkbox

    def test_toggle_unique_ids(self):
        html1 = _call_st_code(code="x = 1", language="python")
        html2 = _call_st_code(code="y = 2", language="python")
        # Extract the uid from id="stx-wrap-..."
        import re
        ids1 = re.findall(r'id="(stx-wrap-[^"]+)"', html1)
        ids2 = re.findall(r'id="(stx-wrap-[^"]+)"', html2)
        assert ids1, "Should have at least one stx-wrap id"
        assert ids2, "Should have at least one stx-wrap id"
        assert ids1[0] != ids2[0], "Two calls should produce different IDs"


# ---------------------------------------------------------------------------
# Fallback path — Pygments not available (simulated via ImportError)
# ---------------------------------------------------------------------------

class TestStCodeFallbackNoPygments:
    def _call_without_pygments(self, **kwargs):
        """Simulate ImportError for pygments inside st_code."""
        from streamtex.code import st_code
        captured = []

        original_import = __builtins__.__import__ if hasattr(__builtins__, '__import__') else __import__

        def _fake_import(name, *args, **kw):
            if name == "pygments":
                raise ImportError("No module named 'pygments'")
            return original_import(name, *args, **kw)

        with patch("builtins.__import__", side_effect=_fake_import), \
             patch("streamtex.code._render", side_effect=captured.append):
            st_code(**kwargs)

        assert len(captured) == 1
        return captured[0]

    def test_fallback_uses_pre_tag(self):
        # Patch the pygments import inside the function to raise ImportError
        import importlib
        with patch.dict(sys.modules, {"pygments": None,
                                       "pygments.highlight": None,
                                       "pygments.lexers": None,
                                       "pygments.formatters": None}):
            # Re-import to pick up the mocked modules
            if "streamtex.code" in sys.modules:
                del sys.modules["streamtex.code"]
            from streamtex.code import st_code
            captured = []
            with patch("streamtex.code._render", side_effect=captured.append):
                st_code(code="x = 42", language="python")
            html = captured[0]
            assert "<pre" in html
            assert "x = 42" in html

    def test_fallback_line_numbers_included(self):
        with patch.dict(sys.modules, {"pygments": None,
                                       "pygments.highlight": None,
                                       "pygments.lexers": None,
                                       "pygments.formatters": None}):
            if "streamtex.code" in sys.modules:
                del sys.modules["streamtex.code"]
            from streamtex.code import st_code
            captured = []
            with patch("streamtex.code._render", side_effect=captured.append):
                st_code(code="a = 1\nb = 2", language="python", line_numbers=True)
            html = captured[0]
            # Line numbers appear as "   1 " prefix in fallback
            assert "1 " in html
            assert "2 " in html

    def test_fallback_no_line_numbers_when_disabled(self):
        with patch.dict(sys.modules, {"pygments": None,
                                       "pygments.highlight": None,
                                       "pygments.lexers": None,
                                       "pygments.formatters": None}):
            if "streamtex.code" in sys.modules:
                del sys.modules["streamtex.code"]
            from streamtex.code import st_code
            captured = []
            with patch("streamtex.code._render", side_effect=captured.append):
                st_code(code="a = 1", language="python", line_numbers=False)
            html = captured[0]
            # No numeric line prefix — just the code
            assert "   1 " not in html
            assert "a = 1" in html

    def test_fallback_custom_font_size_in_pre(self):
        with patch.dict(sys.modules, {"pygments": None,
                                       "pygments.highlight": None,
                                       "pygments.lexers": None,
                                       "pygments.formatters": None}):
            if "streamtex.code" in sys.modules:
                del sys.modules["streamtex.code"]
            from streamtex.code import st_code
            captured = []
            with patch("streamtex.code._render", side_effect=captured.append):
                st_code(code="pass", language="python", font_size="12pt")
            html = captured[0]
            assert "12pt" in html

    def teardown_method(self, method):
        # Restore the real streamtex.code module after patching sys.modules
        if "streamtex.code" in sys.modules:
            del sys.modules["streamtex.code"]
