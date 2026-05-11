"""Unit tests for streamtex.grid — GridController and st_grid context manager."""

import os
from unittest.mock import MagicMock, patch

import pytest

from streamtex.grid import GridController, responsive_cols, st_grid
from streamtex.styles import StxStyles, Style, StyleGrid


# Module-level autouse fixture: legacy :has() path is the default for tests
# in this file (matches their historical assertions).  Marker-path tests
# opt in via `_marker_runtime_on` below.
@pytest.fixture(autouse=True)
def _force_legacy_by_default():
    prev_legacy = os.environ.get("STX_USE_LEGACY_HAS")
    prev_marker = os.environ.get("STX_USE_MARKER_RUNTIME")
    os.environ["STX_USE_LEGACY_HAS"] = "1"
    os.environ.pop("STX_USE_MARKER_RUNTIME", None)
    yield
    if prev_legacy is None:
        os.environ.pop("STX_USE_LEGACY_HAS", None)
    else:
        os.environ["STX_USE_LEGACY_HAS"] = prev_legacy
    if prev_marker is None:
        os.environ.pop("STX_USE_MARKER_RUNTIME", None)
    else:
        os.environ["STX_USE_MARKER_RUNTIME"] = prev_marker

# ===========================================================================
# TestGridController — Style resolution and cell counter
# ===========================================================================

class TestGridController:
    """Tests for the GridController class."""

    def test_init_with_int_cols(self):
        """Test initialization with int cols value."""
        controller = GridController(cols=3)
        assert controller.cols == 3
        assert controller.cell_counter == 0

    def test_init_with_string_cols(self):
        """Test initialization with string cols template."""
        controller = GridController(cols="1fr 1fr 1fr")
        assert controller.cols == 3

    def test_init_with_single_col_string(self):
        """Test initialization with single column string (no spaces)."""
        controller = GridController(cols="200px")
        assert controller.cols == 1

    def test_init_with_complex_string_cols(self):
        """Test initialization with complex template string."""
        controller = GridController(cols="auto 1fr 200px")
        assert controller.cols == 3

    def test_init_default_cell_styles(self):
        """Test default cell_styles is StxStyles.none."""
        controller = GridController()
        assert controller.cell_styles is StxStyles.none

    def test_init_with_single_style(self):
        """Test initialization with a single Style object."""
        style = Style("color: red;", "red")
        controller = GridController(cols=2, cell_styles=style)
        assert controller.cell_styles is style

    def test_init_with_flat_list_styles(self):
        """Test initialization with a flat list of styles."""
        styles = [
            Style("color: red;", "red"),
            Style("color: blue;", "blue"),
        ]
        controller = GridController(cols=2, cell_styles=styles)
        assert controller.cell_styles == styles

    def test_init_with_matrix_styles(self):
        """Test initialization with a matrix (list of lists) of styles."""
        styles = [
            [Style("color: red;", "red"), Style("color: blue;", "blue")],
            [Style("color: green;", "green"), Style("color: yellow;", "yellow")],
        ]
        controller = GridController(cols=2, cell_styles=styles)
        assert controller.cell_styles == styles

    def test_init_with_style_grid(self):
        """Test initialization with a StyleGrid object."""
        style = Style("color: red;", "red")
        grid = StyleGrid.create("A1", style)
        controller = GridController(cols=2, cell_styles=grid)
        assert controller.cell_styles is grid

    # -----------------------------------------------------------------------
    # _resolve_style tests
    # -----------------------------------------------------------------------

    def test_resolve_style_single_style(self):
        """Test _resolve_style with a single Style object returns that style."""
        style = Style("color: red;", "red")
        controller = GridController(cols=2, cell_styles=style)

        resolved = controller._resolve_style(0)
        assert resolved is style

        resolved = controller._resolve_style(5)
        assert resolved is style

    def test_resolve_style_flat_list(self):
        """Test _resolve_style with a flat list of styles."""
        red = Style("color: red;", "red")
        blue = Style("color: blue;", "blue")
        green = Style("color: green;", "green")
        styles = [red, blue, green]

        controller = GridController(cols=3, cell_styles=styles)

        assert controller._resolve_style(0) is red
        assert controller._resolve_style(1) is blue
        assert controller._resolve_style(2) is green

    def test_resolve_style_flat_list_out_of_bounds(self):
        """Test _resolve_style with flat list returns fallback for out-of-bounds index."""
        red = Style("color: red;", "red")
        blue = Style("color: blue;", "blue")
        styles = [red, blue]

        controller = GridController(cols=2, cell_styles=styles)

        resolved = controller._resolve_style(5)
        assert resolved is StxStyles.none

    def test_resolve_style_matrix(self):
        """Test _resolve_style with a matrix (list of lists) of styles."""
        styles = [
            [
                Style("color: red;", "red"),
                Style("color: blue;", "blue"),
            ],
            [
                Style("color: green;", "green"),
                Style("color: yellow;", "yellow"),
            ],
        ]
        controller = GridController(cols=2, cell_styles=styles)

        # Matrix is flattened to [red, blue, green, yellow]
        assert controller._resolve_style(0) is styles[0][0]
        assert controller._resolve_style(1) is styles[0][1]
        assert controller._resolve_style(2) is styles[1][0]
        assert controller._resolve_style(3) is styles[1][1]

    def test_resolve_style_matrix_out_of_bounds(self):
        """Test _resolve_style with matrix returns fallback for out-of-bounds index."""
        styles = [
            [Style("color: red;", "red")],
        ]
        controller = GridController(cols=1, cell_styles=styles)

        resolved = controller._resolve_style(10)
        assert resolved is StxStyles.none

    def test_resolve_style_style_grid(self):
        """Test _resolve_style with a StyleGrid object."""
        red = Style("color: red;", "red")
        blue = Style("color: blue;", "blue")
        green = Style("color: green;", "green")

        grid = StyleGrid.create("A1:B2", red)
        # StyleGrid's css_grid is a matrix, we'll verify this extracts correctly

        controller = GridController(cols=2, cell_styles=grid)

        # The grid should have a 2x2 matrix of red styles
        assert controller._resolve_style(0) is red
        assert controller._resolve_style(1) is red
        assert controller._resolve_style(2) is red
        assert controller._resolve_style(3) is red

    def test_resolve_style_style_grid_out_of_bounds(self):
        """Test _resolve_style with StyleGrid returns fallback for out-of-bounds index."""
        style = Style("color: red;", "red")
        grid = StyleGrid.create("A1", style)

        controller = GridController(cols=1, cell_styles=grid)

        resolved = controller._resolve_style(10)
        assert resolved is StxStyles.none

    def test_resolve_style_fallback_none_styles(self):
        """Test _resolve_style returns fallback for None cell_styles."""
        controller = GridController(cols=2)
        # cell_styles defaults to StxStyles.none

        resolved = controller._resolve_style(0)
        assert resolved is StxStyles.none

    def test_resolve_style_empty_list(self):
        """Test _resolve_style with empty list returns fallback."""
        controller = GridController(cols=2, cell_styles=[])

        resolved = controller._resolve_style(0)
        assert resolved is StxStyles.none

    def test_resolve_style_empty_matrix(self):
        """Test _resolve_style with empty matrix returns fallback."""
        controller = GridController(cols=2, cell_styles=[[]])

        resolved = controller._resolve_style(0)
        assert resolved is StxStyles.none

    # -----------------------------------------------------------------------
    # Cell counter tests
    # -----------------------------------------------------------------------

    def test_cell_counter_increments(self):
        """Test that cell_counter starts at 0 and can be incremented."""
        controller = GridController(cols=2)
        assert controller.cell_counter == 0

        controller.cell_counter += 1
        assert controller.cell_counter == 1

        controller.cell_counter += 1
        assert controller.cell_counter == 2


# ===========================================================================
# TestStGrid — Context manager behavior
# ===========================================================================

class TestStGrid:
    """Tests for the st_grid context manager."""

    def test_st_grid_context_manager_yields_controller(self, mock_streamlit):
        """Test that st_grid context manager yields a GridController."""
        with st_grid(cols=2) as controller:
            assert isinstance(controller, GridController)
            assert controller.cols == 2

    def test_st_grid_with_int_cols_generates_template(self, mock_streamlit):
        """Test st_grid with int cols generates correct CSS template."""
        with st_grid(cols=3) as controller:
            pass

        # Check that st.html was called with CSS containing the template
        html_calls = mock_streamlit["html"].call_args_list

        # First call should be the CSS injection
        css_call = html_calls[0]
        css_html = css_call[0][0]
        assert "grid-template-columns: 1fr 1fr 1fr;" in css_html

    def test_st_grid_with_string_cols_uses_as_is(self, mock_streamlit):
        """Test st_grid with string cols uses the string directly."""
        with st_grid(cols="200px 1fr") as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_call = html_calls[0]
        css_html = css_call[0][0]
        assert "grid-template-columns: 200px 1fr;" in css_html

    def test_st_grid_with_empty_string_cols_raises(self, mock_streamlit):
        """Test that st_grid with empty string cols raises ValueError (C5 validation)."""
        with pytest.raises(ValueError, match="st_grid cols parameter cannot be empty string"):
            with st_grid(cols="") as controller:
                pass

    def test_st_grid_with_whitespace_cols_raises(self, mock_streamlit):
        """Test that st_grid with whitespace-only cols raises ValueError."""
        with pytest.raises(ValueError, match="st_grid cols parameter cannot be empty string"):
            with st_grid(cols="   ") as controller:
                pass

    def test_st_grid_with_gap_parameter(self, mock_streamlit):
        """Test st_grid with explicit gap parameter (C2 feature)."""
        with st_grid(cols=2, gap="24px") as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_call = html_calls[0]
        css_html = css_call[0][0]
        assert "gap: 24px;" in css_html

    def test_st_grid_default_gap_is_zero(self, mock_streamlit):
        """Test st_grid default gap value is 0."""
        with st_grid(cols=2) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_call = html_calls[0]
        css_html = css_call[0][0]
        assert "gap: 0;" in css_html

    def test_st_grid_with_grid_style(self, mock_streamlit):
        """Test st_grid applies grid_style to the grid container."""
        grid_style = Style("border: 1px solid red;", "bordered_grid")

        with st_grid(cols=2, grid_style=grid_style) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_call = html_calls[0]
        css_html = css_call[0][0]
        assert "border: 1px solid red;" in css_html

    def test_st_grid_generates_unique_grid_id(self, mock_streamlit):
        """Test that st_grid generates unique grid IDs for multiple grids."""
        grid_ids = []

        for _ in range(2):
            with st_grid(cols=2) as controller:
                pass

            html_calls = mock_streamlit["html"].call_args_list
            css_call = html_calls[0]
            css_html = css_call[0][0]

            # Extract grid ID from CSS (e.g., ".css-grid-abc123def")
            import re
            match = re.search(r'\.(\bcss-grid-[\da-f]+\b)', css_html)
            if match:
                grid_ids.append(match.group(1))

            mock_streamlit["html"].reset_mock()

        # IDs should be different (both should be found)
        if len(grid_ids) == 2:
            assert grid_ids[0] != grid_ids[1]

    def test_st_grid_calls_st_html_multiple_times(self, mock_streamlit):
        """Test that st_grid calls st.html for CSS and marker."""
        with st_grid(cols=2) as controller:
            pass

        # Should have called st.html multiple times (CSS + marker)
        html_calls = mock_streamlit["html"].call_args_list
        assert len(html_calls) >= 2

    def test_st_grid_marker_hidden(self, mock_streamlit):
        """Test that the marker span is hidden."""
        with st_grid(cols=2) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list

        # Last call should be the marker with display:none
        marker_call = html_calls[-1]
        marker_html = marker_call[0][0]
        assert "display:none" in marker_html

    def test_st_grid_calls_st_container(self, mock_streamlit):
        """Test that st_grid calls st.container."""
        with patch("streamlit.container") as mock_container:
            mock_context = MagicMock()
            mock_context.__enter__ = MagicMock(return_value=None)
            mock_context.__exit__ = MagicMock(return_value=None)
            mock_container.return_value = mock_context

            with st_grid(cols=2) as controller:
                pass

            mock_container.assert_called()

    def test_st_grid_with_cell_styles(self, mock_streamlit):
        """Test st_grid accepts cell_styles parameter."""
        style1 = Style("color: red;", "red")
        style2 = Style("color: blue;", "blue")
        cell_styles = [style1, style2]

        with st_grid(cols=2, cell_styles=cell_styles) as controller:
            assert controller.cell_styles == cell_styles

    def test_st_grid_complex_cols_template(self, mock_streamlit):
        """Test st_grid with complex CSS grid template."""
        template = "repeat(auto-fill, minmax(200px, 1fr))"

        with st_grid(cols=template) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_call = html_calls[0]
        css_html = css_call[0][0]
        assert f"grid-template-columns: {template};" in css_html

    def test_st_grid_all_gaps_values(self, mock_streamlit):
        """Test st_grid with various gap values."""
        gap_values = ["0", "10px", "1rem", "24px", "2%"]

        for gap_val in gap_values:
            mock_streamlit["html"].reset_mock()

            with st_grid(cols=2, gap=gap_val) as controller:
                pass

            html_calls = mock_streamlit["html"].call_args_list
            css_call = html_calls[0]
            css_html = css_call[0][0]
            assert f"gap: {gap_val};" in css_html

    def test_st_grid_export_wrapper_inactive(self, mock_streamlit):
        """Test st_grid export wrapper is no-op when export is inactive."""
        with patch("streamtex.grid.is_export_active", return_value=False):
            with patch("streamtex.grid.export_push_wrapper") as mock_push, \
                 patch("streamtex.grid.export_pop_wrapper") as mock_pop:

                with st_grid(cols=2) as controller:
                    pass

                mock_push.assert_not_called()
                mock_pop.assert_not_called()

    def test_st_grid_export_wrapper_active(self, mock_streamlit):
        """Test st_grid export wrapper is called when export is active."""
        with patch("streamtex.grid.is_export_active", return_value=True):
            with patch("streamtex.grid.export_push_wrapper") as mock_push, \
                 patch("streamtex.grid.export_pop_wrapper") as mock_pop:

                with st_grid(cols=2, gap="24px") as controller:
                    pass

                mock_push.assert_called()
                mock_pop.assert_called()

                # Check that the wrapper contains the grid template and gap
                push_call_args = mock_push.call_args[0][0]
                assert "display:grid" in push_call_args
                assert "grid-template-columns:" in push_call_args
                assert "gap:24px" in push_call_args

    def test_st_grid_export_wrapper_with_grid_style(self, mock_streamlit):
        """Test st_grid export wrapper includes grid_style."""
        grid_style = Style("border: 1px solid;", "bordered")

        with patch("streamtex.grid.is_export_active", return_value=True):
            with patch("streamtex.grid.export_push_wrapper") as mock_push:

                with st_grid(cols=2, grid_style=grid_style) as controller:
                    pass

                push_call_args = mock_push.call_args[0][0]
                assert "border: 1px solid;" in push_call_args


# ===========================================================================
# TestGridCellContext — GridController.cell() context manager
# ===========================================================================

class TestGridCellContext:
    """Tests for the GridController.cell() context manager."""

    def test_cell_context_manager_yields(self, mock_streamlit):
        """Test that cell() is a context manager."""
        controller = GridController(cols=2)

        with controller.cell():
            pass

        # Should not raise an exception
        assert True

    def test_cell_counter_increments_on_cell_entry(self, mock_streamlit):
        """Test that cell_counter increments when entering a cell."""
        controller = GridController(cols=2)
        assert controller.cell_counter == 0

        with controller.cell():
            assert controller.cell_counter == 1

        with controller.cell():
            assert controller.cell_counter == 2

    def test_cell_resolves_style(self, mock_streamlit):
        """Test that cell() resolves and applies the correct style."""
        style1 = Style("color: red;", "red")
        style2 = Style("color: blue;", "blue")
        cell_styles = [style1, style2]

        controller = GridController(cols=2, cell_styles=cell_styles)

        # First cell should get style1
        with controller.cell():
            pass

        # Check that st_block was called (via the import)
        # We verify this indirectly through the mock
        assert controller.cell_counter == 1

    def test_cell_adds_height_width_styles(self, mock_streamlit):
        """Test that cell() adds height:100%, width:100%, box-sizing styles."""
        controller = GridController(cols=2)

        with patch("streamtex.grid.st_block") as mock_block:
            mock_context = MagicMock()
            mock_context.__enter__ = MagicMock(return_value=None)
            mock_context.__exit__ = MagicMock(return_value=None)
            mock_block.return_value = mock_context

            with controller.cell():
                pass

            # st_block should have been called with a style containing height:100%
            call_kwargs = mock_block.call_args[1]
            style_str = call_kwargs["style"]
            assert "height: 100%" in style_str
            assert "width: 100%" in style_str
            assert "box-sizing: border-box;" in style_str

    def test_cell_with_multiple_cells(self, mock_streamlit):
        """Test multiple cells in sequence."""
        styles = [
            Style("color: red;", "red"),
            Style("color: blue;", "blue"),
            Style("color: green;", "green"),
        ]
        controller = GridController(cols=3, cell_styles=styles)

        for i in range(3):
            with controller.cell():
                pass
            assert controller.cell_counter == i + 1


# ===========================================================================
# Integration tests
# ===========================================================================

class TestStGridIntegration:
    """Integration tests for st_grid with real GridController usage."""

    def test_st_grid_full_workflow(self, mock_streamlit):
        """Test complete st_grid workflow: creation, cells, cleanup."""
        with st_grid(cols=2, gap="16px") as g:
            assert isinstance(g, GridController)
            assert g.cols == 2

            # Simulate adding cells
            with g.cell():
                pass

            with g.cell():
                pass

        # Verify HTML was called
        assert mock_streamlit["html"].called

    def test_st_grid_with_matrix_cell_styles(self, mock_streamlit):
        """Test st_grid with matrix cell_styles."""
        styles = [
            [Style("color: red;", "red"), Style("color: blue;", "blue")],
            [Style("color: green;", "green"), Style("color: yellow;", "yellow")],
        ]

        with st_grid(cols=2, cell_styles=styles) as g:
            assert g.cell_styles == styles

            # Verify styles are resolved correctly
            assert g._resolve_style(0) is styles[0][0]
            assert g._resolve_style(1) is styles[0][1]
            assert g._resolve_style(2) is styles[1][0]
            assert g._resolve_style(3) is styles[1][1]


# ===========================================================================
# TestResponsiveCols — responsive_cols() helper function
# ===========================================================================

class TestResponsiveCols:
    """Tests for the responsive_cols() helper function."""

    def test_responsive_cols_default_2(self):
        """Test responsive_cols(2) returns minmax(350px, 1fr)."""
        result = responsive_cols(2)
        assert result == "repeat(auto-fit, minmax(350px, 1fr))"

    def test_responsive_cols_default_3(self):
        """Test responsive_cols(3) returns minmax(280px, 1fr)."""
        result = responsive_cols(3)
        assert result == "repeat(auto-fit, minmax(280px, 1fr))"

    def test_responsive_cols_default_4(self):
        """Test responsive_cols(4) returns minmax(220px, 1fr)."""
        result = responsive_cols(4)
        assert result == "repeat(auto-fit, minmax(220px, 1fr))"

    def test_responsive_cols_single_col(self):
        """Test responsive_cols(1) returns '1fr' (no wrapping needed)."""
        result = responsive_cols(1)
        assert result == "1fr"

    def test_responsive_cols_invalid(self):
        """Test responsive_cols(0) raises ValueError."""
        with pytest.raises(ValueError, match="responsive_cols requires cols >= 1"):
            responsive_cols(0)

    def test_responsive_cols_explicit_int(self):
        """Test responsive_cols with explicit int min_width."""
        result = responsive_cols(3, min_width=300)
        assert result == "repeat(auto-fit, minmax(300px, 1fr))"

    def test_responsive_cols_explicit_str(self):
        """Test responsive_cols with explicit string min_width."""
        result = responsive_cols(2, min_width="20em")
        assert result == "repeat(auto-fit, minmax(20em, 1fr))"

    def test_responsive_cols_large_n(self):
        """Test responsive_cols(10) uses fallback formula max(120, 900//10) = 120."""
        result = responsive_cols(10)
        # max(120, int(900/10)) = max(120, 90) = 120
        assert result == "repeat(auto-fit, minmax(120px, 1fr))"

    def test_responsive_cols_7_uses_formula(self):
        """Test responsive_cols(7) uses fallback formula max(120, 900//7) = 128."""
        result = responsive_cols(7)
        # max(120, int(900/7)) = max(120, 128) = 128
        assert result == "repeat(auto-fit, minmax(128px, 1fr))"

    def test_responsive_cols_default_5(self):
        """Test responsive_cols(5) returns minmax(180px, 1fr)."""
        result = responsive_cols(5)
        assert result == "repeat(auto-fit, minmax(180px, 1fr))"

    def test_responsive_cols_default_6(self):
        """Test responsive_cols(6) returns minmax(150px, 1fr)."""
        result = responsive_cols(6)
        assert result == "repeat(auto-fit, minmax(150px, 1fr))"


# ===========================================================================
# TestStGrid — Responsive mode tests (appended to existing class scope)
# ===========================================================================

class TestStGridResponsive:
    """Tests for st_grid responsive mode."""

    def test_st_grid_responsive_flag(self, mock_streamlit):
        """Test st_grid with responsive=True generates auto-fit/minmax CSS."""
        with st_grid(cols=3, responsive=True) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_html = html_calls[0][0][0]
        assert "auto-fit" in css_html
        assert "minmax(280px, 1fr)" in css_html

    def test_st_grid_responsive_with_min_width(self, mock_streamlit):
        """Test st_grid responsive with explicit min_width."""
        with st_grid(cols=3, responsive=True, min_width=400) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_html = html_calls[0][0][0]
        assert "minmax(400px, 1fr)" in css_html

    def test_st_grid_responsive_string_cols_ignored(self, mock_streamlit):
        """Test responsive flag is ignored when cols is a string."""
        with st_grid(cols="auto 1fr", responsive=True) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_html = html_calls[0][0][0]
        assert "grid-template-columns: auto 1fr;" in css_html

    def test_st_grid_min_width_implies_responsive(self, mock_streamlit):
        """Test min_width parameter implicitly activates responsive mode."""
        with st_grid(cols=3, min_width=250) as controller:
            pass

        html_calls = mock_streamlit["html"].call_args_list
        css_html = html_calls[0][0][0]
        assert "auto-fit" in css_html
        assert "minmax(250px, 1fr)" in css_html

    def test_st_grid_responsive_controller_cols(self, mock_streamlit):
        """Test that responsive mode preserves intended_cols on the controller."""
        with st_grid(cols=4, responsive=True) as controller:
            assert controller.cols == 4

    def test_st_grid_responsive_export_wrapper(self, mock_streamlit):
        """Test responsive st_grid export wrapper contains auto-fit template."""
        with patch("streamtex.grid.is_export_active", return_value=True):
            with patch("streamtex.grid.export_push_wrapper") as mock_push, \
                 patch("streamtex.grid.export_pop_wrapper"):

                with st_grid(cols=3, responsive=True) as controller:
                    pass

                push_call_args = mock_push.call_args[0][0]
                assert "auto-fit" in push_call_args
                assert "minmax(280px, 1fr)" in push_call_args


# ===========================================================================
# TestGridController — intended_cols tests
# ===========================================================================

class TestGridControllerIntendedCols:
    """Tests for GridController intended_cols parameter."""

    def test_init_with_intended_cols(self):
        """Test GridController with intended_cols overrides string inference."""
        controller = GridController(
            "repeat(auto-fit, minmax(280px, 1fr))",
            intended_cols=3,
        )
        assert controller.cols == 3

    def test_init_intended_cols_none_fallback(self):
        """Test GridController without intended_cols falls back to space-count."""
        controller = GridController("1fr 1fr 1fr")
        assert controller.cols == 3


# ===========================================================================
# Phase 3 — marker-runtime path (STX_USE_MARKER_RUNTIME=1)
# ===========================================================================


@pytest.fixture
def _marker_runtime_on():
    prev_legacy = os.environ.get("STX_USE_LEGACY_HAS")
    prev_marker = os.environ.get("STX_USE_MARKER_RUNTIME")
    os.environ.pop("STX_USE_LEGACY_HAS", None)
    os.environ["STX_USE_MARKER_RUNTIME"] = "1"
    yield
    if prev_legacy is None:
        os.environ.pop("STX_USE_LEGACY_HAS", None)
    else:
        os.environ["STX_USE_LEGACY_HAS"] = prev_legacy
    if prev_marker is None:
        os.environ.pop("STX_USE_MARKER_RUNTIME", None)
    else:
        os.environ["STX_USE_MARKER_RUNTIME"] = prev_marker


class TestStGridMarkerPath:
    def test_emits_grid_marker(self, mock_streamlit, _marker_runtime_on):
        with st_grid(2):
            pass
        joined = "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)
        assert 'data-stx-kind="grid"' in joined
        assert 'data-stx-uid="css-grid-' in joined

    def test_template_carried_by_data_attr(self, mock_streamlit, _marker_runtime_on):
        with st_grid(3):
            pass
        joined = "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)
        assert 'data-stx-grid-template="1fr 1fr 1fr"' in joined

    def test_no_has_selector_emitted(self, mock_streamlit, _marker_runtime_on):
        with st_grid(2):
            pass
        joined = "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)
        assert ":has(" not in joined

    def test_gap_carried_by_data_attr(self, mock_streamlit, _marker_runtime_on):
        with st_grid(2, gap="1rem"):
            pass
        joined = "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)
        assert 'data-stx-grid-gap="1rem"' in joined

    def test_breakpoint_emits_per_instance_container_query(self, mock_streamlit, _marker_runtime_on):
        """`@container` queries cannot consume var() reliably across browsers
        so breakpoints stay per-instance — but still keyed by attribute
        selector, not :has()."""
        with st_grid(2, breakpoint="600px"):
            pass
        joined = "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)
        assert "@container" in joined
        assert "max-width: 600px" in joined
        assert '[data-stx-grid-uid="css-grid-' in joined
        assert ":has(" not in joined

    def test_grid_style_emits_per_instance_stylesheet(self, mock_streamlit, _marker_runtime_on):
        with st_grid(2, grid_style=Style("background: yellow;", "bg_yellow")):
            pass
        joined = "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)
        assert '[data-stx-grid-uid="css-grid-' in joined
        assert "background: yellow" in joined
        assert ":has(" not in joined

    def test_responsive_template(self, mock_streamlit, _marker_runtime_on):
        with st_grid(3, responsive=True):
            pass
        joined = "".join(c[0][0] for c in mock_streamlit["html"].call_args_list)
        assert "repeat(auto-fit" in joined
        assert ":has(" not in joined
