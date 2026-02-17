"""Tests for the StreamTeX style system."""

import pytest
from streamtex.styles import (
    Style, ListStyle, StyleGrid, StreamTeX_Styles,
    theme, add_css, remove_css,
    Colors, Sizes, Weights, Alignments, Decors, Fonts,
    BackgroundColors, Paddings, Margins, Borders, ContainerSizes,
    Flex, Layouts, Visibility, Positions,
    Text, Container, Titles, ListStyles,
)


class TestStyle:
    """Tests for the Style class."""

    def test_create_empty_style(self):
        s = Style("", "empty")
        assert s.css == ""
        assert s.style_id == "empty"
        assert str(s) == ""

    def test_create_style_with_css(self):
        s = Style("color: red;", "red_text")
        assert s.css == "color: red;"
        assert str(s) == "color: red;"

    def test_style_repr_uses_css_by_default(self):
        s = Style("font-size: 16pt;", "medium")
        assert repr(s) == "font-size: 16pt;"

    def test_style_repr_uses_theme_override(self):
        theme["test_override"] = "color: green;"
        s = Style("color: red;", "test_override")
        assert repr(s) == "color: green;"
        del theme["test_override"]

    def test_style_add_style(self):
        s1 = Style("color: red;", "red")
        s2 = Style("font-weight: bold;", "bold")
        combined = s1 + s2
        assert "color: red;" in str(combined)
        assert "font-weight: bold;" in str(combined)

    def test_style_add_string(self):
        s1 = Style("color: red;", "red")
        combined = s1 + "font-size: 12pt;"
        assert "color: red;" in str(combined)
        assert "font-size: 12pt;" in str(combined)

    def test_style_radd_string(self):
        s1 = Style("color: red;", "red")
        combined = "font-size: 12pt;" + s1
        assert "color: red;" in str(combined)
        assert "font-size: 12pt;" in str(combined)

    def test_style_sub_removes_property(self):
        s1 = Style("color: red; font-weight: bold;", "s1")
        s2 = Style("color: red;", "s2")
        result = s1 - s2
        assert "color" not in str(result)
        assert "font-weight: bold" in str(result)

    def test_style_bool_true(self):
        s = Style("color: red;", "red")
        assert bool(s) is True

    def test_style_bool_false(self):
        s = Style("", "empty")
        assert bool(s) is False

    def test_style_factory_create(self):
        original = Style("color: blue;", "original_id")
        copy = Style.create(original, "new_id")
        assert copy.css == "color: blue;"
        assert copy.style_id == "new_id"


class TestListStyle:
    """Tests for ListStyle."""

    def test_default_symbols(self):
        ls = ListStyle()
        assert ls.symbols == ["●"]

    def test_custom_symbols(self):
        ls = ListStyle(symbols=["▸", "○", "■"])
        assert ls.symbols == ["▸", "○", "■"]

    def test_lvl_cycles_symbols(self):
        ls = ListStyle(symbols=["A", "B", "C"])
        assert ls.lvl(1) == "list-style-type: 'A';"
        assert ls.lvl(2) == "list-style-type: 'B';"
        assert ls.lvl(3) == "list-style-type: 'C';"
        assert ls.lvl(4) == "list-style-type: 'A';"  # Cycles back

    def test_add_merges_symbols(self):
        ls1 = ListStyle(symbols=["A"])
        ls2 = ListStyle(symbols=["B"])
        combined = ls1 + ls2
        assert combined.symbols == ["A", "B"]

    def test_sub_removes_symbols(self):
        ls1 = ListStyle(symbols=["A", "B", "C"])
        ls2 = ListStyle(symbols=["B"])
        result = ls1 - ls2
        assert result.symbols == ["A", "C"]

    def test_factory_create(self):
        original = ListStyle("color: red;", "orig", ["X", "Y"])
        copy = ListStyle.create(original, "copy_id")
        assert copy.symbols == ["X", "Y"]
        assert copy.style_id == "copy_id"


class TestStyleGrid:
    """Tests for StyleGrid."""

    def test_create_single_cell(self):
        s = Style("color: red;", "red")
        grid = StyleGrid.create("A1", s)
        assert grid.css_grid[0][0] is s

    def test_create_range(self):
        s = Style("color: red;", "red")
        grid = StyleGrid.create("A1:B2", s)
        assert len(grid.css_grid) == 2
        assert len(grid.css_grid[0]) == 2
        assert grid.css_grid[0][0] is s
        assert grid.css_grid[0][1] is s
        assert grid.css_grid[1][0] is s
        assert grid.css_grid[1][1] is s

    def test_create_fills_none_for_unspecified_cells(self):
        s = Style("color: red;", "red")
        grid = StyleGrid.create("B2", s, num_rows=3, num_cols=3)
        assert grid.css_grid[0][0] is StreamTeX_Styles.none
        assert grid.css_grid[1][1] is s

    def test_add_grids(self):
        s1 = Style("color: red;", "red")
        s2 = Style("font-size: 16pt;", "medium")
        g1 = StyleGrid.create("A1", s1)
        g2 = StyleGrid.create("A1", s2)
        combined = g1 + g2
        result_css = str(combined.css_grid[0][0])
        assert "color: red;" in result_css
        assert "font-size: 16pt;" in result_css

    def test_dimensions(self):
        s = Style("color: red;", "red")
        grid = StyleGrid.create("A1:C3", s)
        rows, cols = grid._get_dimensions()
        assert rows == 3
        assert cols == 3

    def test_empty_grid_dimensions(self):
        grid = StyleGrid([])
        rows, cols = grid._get_dimensions()
        assert rows == 0
        assert cols == 0

    def test_cell_to_indices(self):
        assert StyleGrid._cell_to_indices("A1") == (0, 0)
        assert StyleGrid._cell_to_indices("B3") == (2, 1)
        assert StyleGrid._cell_to_indices("C1") == (0, 2)

    def test_invalid_cell_raises(self):
        with pytest.raises(ValueError):
            StyleGrid._cell_to_indices("123")

    def test_column_letter_to_index(self):
        assert StyleGrid._column_letter_to_index("A") == 0
        assert StyleGrid._column_letter_to_index("B") == 1
        assert StyleGrid._column_letter_to_index("Z") == 25
        assert StyleGrid._column_letter_to_index("AA") == 26


class TestCssHelpers:
    """Tests for add_css and remove_css."""

    def test_add_css_both(self):
        result = add_css("color: red;", "font-size: 16pt;")
        assert result == "color: red;; font-size: 16pt;"

    def test_add_css_first_only(self):
        result = add_css("color: red;", "")
        assert result == "color: red;"

    def test_add_css_second_only(self):
        result = add_css("", "font-size: 16pt;")
        assert result == "font-size: 16pt;"

    def test_remove_css(self):
        result = remove_css("color: red; font-weight: bold", "color: red")
        assert "color" not in result
        assert "font-weight: bold" in result


class TestPredefinedStyles:
    """Tests for predefined style constants."""

    def test_colors_have_correct_css(self):
        assert "color: Red;" in str(Colors.red)
        assert "color: Blue;" in str(Colors.blue)

    def test_sizes_have_correct_css(self):
        assert "font-size: 16pt;" in str(Sizes.medium_size)
        assert "font-size: 48pt;" in str(Sizes.Large_size)

    def test_size_factory_int(self):
        s = Sizes.size(20)
        assert "font-size: 20pt;" in str(s)

    def test_size_factory_string(self):
        s = Sizes.size("2em")
        assert "font-size: 2em;" in str(s)

    def test_padding_factory(self):
        p = Paddings.size(10)
        assert "padding: 10pt;" in str(p)

    def test_margin_factory(self):
        m = Margins.size(5, 10)
        assert "margin: 5pt 10pt;" in str(m)

    def test_border_color_from_style(self):
        bc = Borders.color(Colors.red)
        assert "border-color: Red;" in str(bc)

    def test_streamtex_styles_aggregation(self):
        assert StreamTeX_Styles.bold is Weights.bold_weight
        assert StreamTeX_Styles.LARGE is Sizes.LARGE_size
        assert str(StreamTeX_Styles.none) == ""

    def test_visibility_styles(self):
        assert "display: none;" in str(Visibility.hidden)
        assert "visibility: visible;" in str(Visibility.visible)
        assert "visibility: hidden;" in str(Visibility.invisible)

    def test_positions_factory(self):
        t = Positions.top(10)
        assert "top: 10px;" in str(t)
        l = Positions.left("5%")
        assert "left: 5%;" in str(l)
