"""Unit tests for streamtex.zoom — add_zoom_options and inject_zoom_logic."""

from unittest.mock import patch, MagicMock, call
import pytest

from streamtex.zoom import add_zoom_options, inject_zoom_logic


# ---------------------------------------------------------------------------
# inject_zoom_logic — CSS injection
# ---------------------------------------------------------------------------

class TestInjectZoomLogicCSS:
    """Test that CSS is injected with the correct page_width."""

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_default_page_width(self, mock_st, mock_comp):
        """Default page_width uses the constant (100%)."""
        inject_zoom_logic(100)
        css_call = mock_st.html.call_args[0][0]
        assert "width: 100% !important" in css_call
        assert "max-width: 100% !important" in css_call

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_custom_page_width(self, mock_st, mock_comp):
        """Custom page_width is reflected in the CSS."""
        inject_zoom_logic(100, page_width="1224pt")
        css_call = mock_st.html.call_args[0][0]
        assert "width: 1224pt !important" in css_call
        assert "max-width: 1224pt !important" in css_call

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_custom_page_width_800px(self, mock_st, mock_comp):
        """Another custom width value."""
        inject_zoom_logic("Fit", page_width="800px")
        css_call = mock_st.html.call_args[0][0]
        assert "width: 800px !important" in css_call


# ---------------------------------------------------------------------------
# inject_zoom_logic — Fit mode
# ---------------------------------------------------------------------------

class TestInjectZoomLogicFit:
    """Test Fit mode JS generation."""

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_fit_uses_min_1(self, mock_st, mock_comp):
        """Fit mode caps zoom at 1 (Math.min(1, ...))."""
        inject_zoom_logic("Fit")
        js_call = mock_comp.call_args[0][0]
        assert "Math.min(1," in js_call

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_fit_uses_resize_observer(self, mock_st, mock_comp):
        """Fit mode uses ResizeObserver."""
        inject_zoom_logic("Fit")
        js_call = mock_comp.call_args[0][0]
        assert "ResizeObserver" in js_call


# ---------------------------------------------------------------------------
# inject_zoom_logic — Fill mode
# ---------------------------------------------------------------------------

class TestInjectZoomLogicFill:
    """Test Fill mode JS generation."""

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_fill_uses_min_2(self, mock_st, mock_comp):
        """Fill mode caps zoom at 2 (Math.min(2, ...))."""
        inject_zoom_logic("Fill")
        js_call = mock_comp.call_args[0][0]
        assert "Math.min(2," in js_call

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_fill_uses_resize_observer(self, mock_st, mock_comp):
        """Fill mode uses ResizeObserver."""
        inject_zoom_logic("Fill")
        js_call = mock_comp.call_args[0][0]
        assert "ResizeObserver" in js_call

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_fill_distinct_from_fit(self, mock_st, mock_comp):
        """Fill mode should NOT contain Math.min(1, ...) — it uses min(2, ...)."""
        inject_zoom_logic("Fill")
        js_call = mock_comp.call_args[0][0]
        assert "Math.min(1," not in js_call
        assert "Math.min(2," in js_call


# ---------------------------------------------------------------------------
# inject_zoom_logic — Fixed zoom
# ---------------------------------------------------------------------------

class TestInjectZoomLogicFixed:
    """Test fixed percentage zoom."""

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_zoom_100(self, mock_st, mock_comp):
        """100% zoom sets CSS variable to 1.0."""
        inject_zoom_logic(100)
        js_call = mock_comp.call_args[0][0]
        assert "1.0" in js_call

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_zoom_50(self, mock_st, mock_comp):
        """50% zoom sets CSS variable to 0.5."""
        inject_zoom_logic(50)
        js_call = mock_comp.call_args[0][0]
        assert "0.5" in js_call

    @patch("streamlit.components.v1.html")
    @patch("streamtex.zoom.st")
    def test_zoom_200(self, mock_st, mock_comp):
        """200% zoom sets CSS variable to 2.0."""
        inject_zoom_logic(200)
        js_call = mock_comp.call_args[0][0]
        assert "2.0" in js_call


# ---------------------------------------------------------------------------
# add_zoom_options — sidebar widget
# ---------------------------------------------------------------------------

class TestAddZoomOptions:
    """Test that add_zoom_options creates the sidebar widget and propagates page_width."""

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_propagates_page_width(self, mock_st, mock_inject):
        """page_width is forwarded to inject_zoom_logic."""
        mock_st.session_state = {"streamtex_zoom": "Fit"}
        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.selectbox = MagicMock(return_value="Fit")

        add_zoom_options(page_width="900px")

        mock_inject.assert_called_once_with("Fit", page_width="900px")

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_default_page_width_none(self, mock_st, mock_inject):
        """Without page_width, None is passed to inject_zoom_logic."""
        mock_st.session_state = {"streamtex_zoom": 100}
        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.selectbox = MagicMock(return_value=100)

        add_zoom_options()

        mock_inject.assert_called_once_with(100, page_width=None)

    @patch("streamtex.zoom.inject_zoom_logic")
    @patch("streamtex.zoom.st")
    def test_fill_in_zoom_levels(self, mock_st, mock_inject):
        """Fill should be one of the available zoom levels."""
        mock_st.session_state = {"streamtex_zoom": "Fill"}
        mock_st.sidebar.__enter__ = MagicMock(return_value=None)
        mock_st.sidebar.__exit__ = MagicMock(return_value=False)
        mock_st.selectbox = MagicMock(return_value="Fill")

        add_zoom_options()

        # The selectbox should offer Fill as an option
        selectbox_call = mock_st.selectbox.call_args
        options = selectbox_call[1].get("options") or selectbox_call[0][1]
        assert "Fill" in options
        assert "Fit" in options
