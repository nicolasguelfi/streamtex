"""Unit tests for streamtex.zoom — page width and CSS zoom."""

from unittest.mock import MagicMock, patch

from streamtex.zoom import (
    _PAGE_WIDTH_KEY,
    _ZOOM_KEY,
    add_zoom_options,
    inject_zoom_logic,
)

# ---------------------------------------------------------------------------
# inject_zoom_logic — CSS output
# ---------------------------------------------------------------------------

class TestInjectZoomLogicCSS:
    """Verify the CSS output of inject_zoom_logic."""

    @patch("streamtex.zoom.st")
    def test_defaults_100_100(self, mock_st):
        inject_zoom_logic(100, 100)
        css_call = mock_st.html.call_args[0][0]
        assert "width: 100%" in css_call
        assert "zoom: 1.0" in css_call

    @patch("streamtex.zoom.st")
    def test_width_80_zoom_150(self, mock_st):
        inject_zoom_logic(80, 150)
        css_call = mock_st.html.call_args[0][0]
        assert "width: 80%" in css_call
        assert "zoom: 1.5" in css_call

    @patch("streamtex.zoom.st")
    def test_width_120_zoom_50(self, mock_st):
        inject_zoom_logic(120, 50)
        css_call = mock_st.html.call_args[0][0]
        assert "width: 120%" in css_call
        assert "zoom: 0.5" in css_call

    @patch("streamtex.zoom.st")
    def test_padding_uses_constant(self, mock_st):
        from streamtex.constants import PAGE_PADDING
        inject_zoom_logic(100, 100)
        css_call = mock_st.html.call_args[0][0]
        assert PAGE_PADDING in css_call

    @patch("streamtex.zoom.st")
    def test_centering_margin_auto(self, mock_st):
        inject_zoom_logic(100, 100)
        css_call = mock_st.html.call_args[0][0]
        assert "margin-left: auto !important" in css_call
        assert "margin-right: auto !important" in css_call

    @patch("streamtex.zoom.st")
    def test_single_st_html_call(self, mock_st):
        """Only one st.html() call (compatible with export guard)."""
        inject_zoom_logic(100, 100)
        assert mock_st.html.call_count == 1


# ---------------------------------------------------------------------------
# inject_zoom_logic — No JS
# ---------------------------------------------------------------------------

class TestInjectZoomLogicNoJS:
    """Verify no JavaScript or components usage."""

    def test_no_components_import(self):
        """zoom.py should not import streamlit.components."""
        import inspect

        import streamtex.zoom as zoom_mod
        source = inspect.getsource(zoom_mod)
        assert "components" not in source

    @patch("streamtex.zoom.st")
    def test_no_script_tag(self, mock_st):
        """Injected CSS should not contain <script> tags."""
        inject_zoom_logic(100, 100)
        css_call = mock_st.html.call_args[0][0]
        assert "<script>" not in css_call
        assert "<script " not in css_call


# ---------------------------------------------------------------------------
# add_zoom_options — sidebar widgets
# ---------------------------------------------------------------------------

class TestAddZoomOptions:
    """Test that add_zoom_options creates widgets and calls inject_zoom_logic."""

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_creates_two_number_inputs(self, mock_st, mock_inject):
        """Should create exactly 2 number_input widgets."""
        mock_st.session_state = {}
        ctx = MagicMock()
        add_zoom_options(container=ctx)
        assert ctx.number_input.call_count == 2

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_default_page_width_80(self, mock_st, mock_inject):
        """default_page_width=80 initializes session_state to 80."""
        mock_st.session_state = {}
        add_zoom_options(default_page_width=80, container=MagicMock())
        assert mock_st.session_state[_PAGE_WIDTH_KEY] == 80

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_does_not_overwrite_existing_state(self, mock_st, mock_inject):
        """Existing session_state values should not be overwritten."""
        mock_st.session_state = {_PAGE_WIDTH_KEY: 60, _ZOOM_KEY: 200}
        add_zoom_options(default_page_width=100, default_zoom=100,
                         container=MagicMock())
        assert mock_st.session_state[_PAGE_WIDTH_KEY] == 60
        assert mock_st.session_state[_ZOOM_KEY] == 200

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_calls_inject_with_session_values(self, mock_st, mock_inject):
        """inject_zoom_logic is called with the session_state values."""
        mock_st.session_state = {_PAGE_WIDTH_KEY: 75, _ZOOM_KEY: 125}
        add_zoom_options(container=MagicMock())
        mock_inject.assert_called_once_with(75, 125)
