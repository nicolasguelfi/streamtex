"""Unit tests for streamtex.zoom — add_zoom_options and inject_zoom_logic."""

from unittest.mock import patch, MagicMock, call
import pytest

from streamtex.zoom import add_zoom_options, inject_zoom_logic, _PAGE_WIDTH_KEY, _ZOOM_KEY


# ---------------------------------------------------------------------------
# inject_zoom_logic — CSS values
# ---------------------------------------------------------------------------

class TestInjectZoomLogicCSS:
    """Test that CSS is injected with correct width and zoom values."""

    @patch("streamtex.zoom.st")
    def test_defaults_100_100(self, mock_st):
        """Default (100, 100) produces width: 100% and zoom: 1.0."""
        inject_zoom_logic(100, 100)
        css_call = mock_st.html.call_args[0][0]
        assert "width: 100% !important" in css_call
        assert "max-width: 100% !important" in css_call
        assert "zoom: 1.0" in css_call

    @patch("streamtex.zoom.st")
    def test_width_80_zoom_150(self, mock_st):
        """Width 80%, Zoom 150% → width: 80%, zoom: 1.5."""
        inject_zoom_logic(80, 150)
        css_call = mock_st.html.call_args[0][0]
        assert "width: 80% !important" in css_call
        assert "max-width: 80% !important" in css_call
        assert "zoom: 1.5" in css_call

    @patch("streamtex.zoom.st")
    def test_width_120_zoom_50(self, mock_st):
        """Width 120%, Zoom 50% → width: 120%, zoom: 0.5."""
        inject_zoom_logic(120, 50)
        css_call = mock_st.html.call_args[0][0]
        assert "width: 120% !important" in css_call
        assert "max-width: 120% !important" in css_call
        assert "zoom: 0.5" in css_call

    @patch("streamtex.zoom.st")
    def test_padding_uses_constant(self, mock_st):
        """Padding should use PAGE_PADDING constant with responsive var()."""
        inject_zoom_logic(100, 100)
        css_call = mock_st.html.call_args[0][0]
        assert "padding-left: var(--stx-page-padding, 36pt) !important" in css_call
        assert "padding-right: var(--stx-page-padding, 36pt) !important" in css_call

    @patch("streamtex.zoom.st")
    def test_centering_margin_auto(self, mock_st):
        """Page should be centered with margin: auto."""
        inject_zoom_logic(80, 100)
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
        import streamtex.zoom as zoom_mod
        import inspect
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
    """Test that add_zoom_options creates sidebar widgets and calls inject_zoom_logic."""

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_creates_two_number_inputs(self, mock_st, mock_inject):
        """Should create exactly 2 number_input widgets."""
        mock_st.session_state = {}
        col1 = MagicMock()
        col2 = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[col1, col2])
        col1.__enter__ = MagicMock(return_value=None)
        col1.__exit__ = MagicMock(return_value=False)
        col2.__enter__ = MagicMock(return_value=None)
        col2.__exit__ = MagicMock(return_value=False)

        add_zoom_options()

        assert mock_st.number_input.call_count == 2

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_default_page_width_80(self, mock_st, mock_inject):
        """default_page_width=80 initializes session_state to 80."""
        mock_st.session_state = {}
        col1 = MagicMock()
        col2 = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[col1, col2])
        col1.__enter__ = MagicMock(return_value=None)
        col1.__exit__ = MagicMock(return_value=False)
        col2.__enter__ = MagicMock(return_value=None)
        col2.__exit__ = MagicMock(return_value=False)

        add_zoom_options(default_page_width=80)

        assert mock_st.session_state[_PAGE_WIDTH_KEY] == 80

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_does_not_overwrite_existing_state(self, mock_st, mock_inject):
        """Existing session_state values should not be overwritten."""
        mock_st.session_state = {_PAGE_WIDTH_KEY: 60, _ZOOM_KEY: 200}
        col1 = MagicMock()
        col2 = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[col1, col2])
        col1.__enter__ = MagicMock(return_value=None)
        col1.__exit__ = MagicMock(return_value=False)
        col2.__enter__ = MagicMock(return_value=None)
        col2.__exit__ = MagicMock(return_value=False)

        add_zoom_options(default_page_width=100, default_zoom=100)

        # Values should remain unchanged
        assert mock_st.session_state[_PAGE_WIDTH_KEY] == 60
        assert mock_st.session_state[_ZOOM_KEY] == 200

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_calls_inject_with_session_values(self, mock_st, mock_inject):
        """inject_zoom_logic is called with the session_state values."""
        mock_st.session_state = {_PAGE_WIDTH_KEY: 75, _ZOOM_KEY: 125}
        col1 = MagicMock()
        col2 = MagicMock()
        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[col1, col2])
        col1.__enter__ = MagicMock(return_value=None)
        col1.__exit__ = MagicMock(return_value=False)
        col2.__enter__ = MagicMock(return_value=None)
        col2.__exit__ = MagicMock(return_value=False)

        add_zoom_options()

        mock_inject.assert_called_once_with(75, 125)
