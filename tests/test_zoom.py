"""Unit tests for streamtex.zoom — page width and CSS zoom."""

from unittest.mock import MagicMock, patch

from streamtex.zoom import (
    _PAGE_WIDTH_KEY,
    _ZOOM_KEY,
    add_zoom_options,
    inject_zoom_logic,
)

# ---------------------------------------------------------------------------
# inject_zoom_logic — CSS output (fixed zoom)
# ---------------------------------------------------------------------------

class TestInjectZoomLogicCSS:
    """Verify the CSS output of inject_zoom_logic with fixed zoom values."""

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
        """Fixed zoom: only one st.html() call (compatible with export guard)."""
        inject_zoom_logic(100, 100)
        assert mock_st.html.call_count == 1

    @patch("streamtex.zoom.st")
    def test_no_script_tag_fixed_zoom(self, mock_st):
        """Fixed zoom CSS should not contain <script> tags."""
        inject_zoom_logic(100, 100)
        css_call = mock_st.html.call_args[0][0]
        assert "<script>" not in css_call


# ---------------------------------------------------------------------------
# inject_zoom_logic — zoom="fit"
# ---------------------------------------------------------------------------

class TestInjectZoomFit:
    """Verify JS output for zoom='fit'."""

    @patch("streamtex.zoom.components")
    @patch("streamtex.zoom.st")
    def test_fit_uses_components_html(self, mock_st, mock_components):
        """zoom='fit' uses components.html() (for <script> support)."""
        inject_zoom_logic(100, "fit")
        # Should NOT use st.html (no CSS-only call)
        assert mock_st.html.call_count == 0
        # Should use components.html (for JS execution)
        assert mock_components.html.call_count == 1

    @patch("streamtex.zoom.components")
    @patch("streamtex.zoom.st")
    def test_fit_contains_script(self, mock_st, mock_components):
        """zoom='fit' output contains <script> for auto-fit calculation."""
        inject_zoom_logic(100, "fit")
        js_call = mock_components.html.call_args[0][0]
        assert "<script>" in js_call

    @patch("streamtex.zoom.components")
    @patch("streamtex.zoom.st")
    def test_fit_contains_width_css(self, mock_st, mock_components):
        """zoom='fit' still includes width CSS."""
        inject_zoom_logic(80, "fit")
        js_call = mock_components.html.call_args[0][0]
        assert "width: 80%" in js_call

    @patch("streamtex.zoom.components")
    @patch("streamtex.zoom.st")
    def test_fit_contains_resize_observer(self, mock_st, mock_components):
        """zoom='fit' uses resize handler for re-fit on viewport change."""
        inject_zoom_logic(100, "fit")
        js_call = mock_components.html.call_args[0][0]
        assert "resize" in js_call

    @patch("streamtex.zoom.components")
    @patch("streamtex.zoom.st")
    def test_fit_contains_cleanup(self, mock_st, mock_components):
        """zoom='fit' registers cleanup for next injection."""
        inject_zoom_logic(100, "fit")
        js_call = mock_components.html.call_args[0][0]
        assert "_stxZoomFitCleanup" in js_call

    @patch("streamtex.zoom.components")
    @patch("streamtex.zoom.st")
    def test_fit_contains_scroll_height(self, mock_st, mock_components):
        """zoom='fit' measures scrollHeight to determine content height."""
        inject_zoom_logic(100, "fit")
        js_call = mock_components.html.call_args[0][0]
        assert "scrollHeight" in js_call


# ---------------------------------------------------------------------------
# add_zoom_options — sidebar widgets
# ---------------------------------------------------------------------------

class TestAddZoomOptions:
    """Test that add_zoom_options creates widgets and calls inject_zoom_logic."""

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_creates_two_number_inputs(self, mock_st, mock_inject):
        """Should create exactly 2 number_input widgets for fixed zoom."""
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

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_fit_zoom_disables_number_input(self, mock_st, mock_inject):
        """When zoom='fit', Zoom% number_input is disabled (greyed out)."""
        mock_st.session_state = {_ZOOM_KEY: "fit"}
        ctx = MagicMock()
        add_zoom_options(container=ctx)
        # 2 number_inputs: Width% (active) + Zoom% (disabled)
        assert ctx.number_input.call_count == 2
        # The second call (Zoom%) should be disabled
        zoom_call = ctx.number_input.call_args_list[1]
        assert zoom_call.kwargs.get("disabled") is True

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_fit_zoom_calls_inject_with_fit(self, mock_st, mock_inject):
        """inject_zoom_logic receives 'fit' when zoom='fit'."""
        mock_st.session_state = {_PAGE_WIDTH_KEY: 100, _ZOOM_KEY: "fit"}
        add_zoom_options(container=MagicMock())
        mock_inject.assert_called_once_with(100, "fit")
