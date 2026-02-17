"""Core style primitives: Style, ListStyle, StyleGrid, CSS helpers, theme."""

from typing import List, Tuple, Optional, Union
import re


theme = {}
'''The theme style dictionary.
Example: dark = {
    "red_02" : "color: #660000;",
    "pink_01": "color: #d6fc00;"
}'''


def add_css(str1: str, str2: str):
    '''Concatenates two css strings with a ";" in between.'''
    if str1 and str2:
        return str1 + "; " + str2
    elif str1:
        return str1
    else:
        return str2


def remove_css(str1: str, str2: str):
    '''Removes one css string (str2) from another (str1) if present.'''
    props1 = [prop.strip() for prop in str1.split(';') if prop.strip()]
    props2 = [prop.strip() for prop in str2.split(';') if prop.strip()]

    prop_names2 = set()
    for prop in props2:
        match = re.match(r'^([^:]+):', prop)
        if match:
            prop_name = match.group(1).strip()
            prop_names2.add(prop_name)

    new_props1 = []
    for prop in props1:
        match = re.match(r'^([^:]+):', prop)
        if match:
            prop_name = match.group(1).strip()
            if prop_name not in prop_names2:
                new_props1.append(prop)
        else:
            new_props1.append(prop)

    return '; '.join(new_props1)


class Style:
    """Defines a style, encapsulating a string of (maybe) multiple CSS in-line styles, with a global theme."""
    def __init__(self, css: str, style_id: str = ""):
        '''The raw CSS definition'''
        self.css = css
        '''The ID used to look up theme overrides'''
        self.style_id = style_id

    @classmethod
    def create(cls, style, style_id: str):
        """Factory method: create a new Style from an existing one, overriding the style_id."""
        return cls(style.css, style_id)

    def __add__(self, other):
        if isinstance(other, Style):
            combined_css = add_css(str(self), str(other))
            new_id = f"{self.style_id} {other.style_id}".strip()
            return Style(combined_css, new_id)
        elif isinstance(other, str):
            combined_css = add_css(str(self), other)
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{self.style_id} {clean_str_id}".strip()
            return Style(combined_css, new_id)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            combined_css = add_css(other, str(self))
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{clean_str_id} {self.style_id}".strip()
            return Style(combined_css, new_id)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Style):
            new_css = remove_css(str(self), str(other))
            new_id = f"{self.style_id}-{other.style_id}".strip()
            return Style(new_css, new_id)
        elif isinstance(other, str):
            new_css = remove_css(str(self), other)
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{self.style_id}-{clean_str_id}".strip()
            return Style(new_css, new_id)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, str):
            new_css = remove_css(other, str(self))
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{clean_str_id}-{self.style_id}".strip()
            return Style(new_css, new_id)
        return NotImplemented

    def __bool__(self):
        return bool(str(self).strip())

    def __repr__(self):
        """If a global theme override exists for self.style_id, use that. Otherwise, fallback to self.css."""
        return theme.get(self.style_id, self.css)


class ListStyle(Style):
    """Defines a style for lists, including custom list symbols for styling levels."""
    def __init__(self, css: str = "", style_id: str = "", symbols: List[str] = None):
        super().__init__(css, style_id)
        self.symbols = symbols if symbols is not None else ["●"]

    @classmethod
    def create(cls, style, style_id: str):
        """Factory method: create a new ListStyle from an existing one, overriding the style_id."""
        return cls(style.css, style_id, style.symbols)

    def __add__(self, other):
        if isinstance(other, Style):
            combined_css = add_css(str(self), str(other))
            new_id = f"{self.style_id} {other.style_id}".strip()
            new_symbols = list(self.symbols)
            if isinstance(other, ListStyle):
                new_symbols.extend(other.symbols)
            return ListStyle(combined_css, new_id, new_symbols)
        elif isinstance(other, str):
            combined_css = add_css(str(self), other)
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{self.style_id} {clean_str_id}".strip()
            return ListStyle(combined_css, new_id, self.symbols)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, str):
            combined_css = add_css(other, str(self))
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{clean_str_id} {self.style_id}".strip()
            return ListStyle(combined_css, new_id, self.symbols)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, Style):
            new_css = remove_css(str(self), str(other))
            new_id = f"{self.style_id}-{other.style_id}".strip()
            new_symbols = list(self.symbols)
            if isinstance(other, ListStyle):
                for sym in other.symbols:
                    if sym in new_symbols:
                        new_symbols.remove(sym)
            return ListStyle(new_css, new_id, new_symbols)
        elif isinstance(other, str):
            new_css = remove_css(str(self), other)
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{self.style_id}-{clean_str_id}".strip()
            return ListStyle(new_css, new_id, self.symbols)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, str):
            new_css = remove_css(other, str(self))
            clean_str_id = other.replace(" ", "").replace(";", "")
            new_id = f"{clean_str_id}-{self.style_id}".strip()
            return ListStyle(new_css, new_id, self.symbols)
        return NotImplemented

    def lvl(self, lvl: int = 1):
        """Returns the CSS for list-style-type based on the nesting level. Cycles through symbols."""
        index = (lvl - 1) % len(self.symbols)
        return f"list-style-type: '{self.symbols[index]}';"


class StyleGrid:
    """Defines a grid of styles applied to the rows/columns of a table or grid."""

    def __init__(self, css_grid: List[List[Style]] = []):
        self.css_grid = css_grid

    def __add__(self, other):
        if isinstance(other, StyleGrid):
            return self._combine_with(other, combine_styles=lambda s1, s2: s1 + s2)
        elif isinstance(other, list):
            return self + StyleGrid(other)
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, StyleGrid):
            return other + self
        elif isinstance(other, list):
            return StyleGrid(other) + self
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, StyleGrid):
            return self._combine_with(other, combine_styles=lambda s1, s2: s1 - s2)
        elif isinstance(other, list):
            return self - StyleGrid(other)
        return NotImplemented

    def __rsub__(self, other):
        if isinstance(other, StyleGrid):
            return other - self
        elif isinstance(other, list):
            return StyleGrid(other) - self
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, StyleGrid):
            return self._combine_with(other, combine_styles=lambda s1, s2: s2 if s2 else s1)
        elif isinstance(other, list):
            return self * StyleGrid(other)
        return NotImplemented

    def __rmul__(self, other):
        if isinstance(other, StyleGrid):
            return other * self
        elif isinstance(other, list):
            return StyleGrid(other) * self
        return NotImplemented

    def _combine_with(self, other, combine_styles):
        # Import here to avoid circular import at module level
        from .base import StreamTeX_Styles
        self_rows, self_cols = self._get_dimensions()
        other_rows, other_cols = other._get_dimensions()

        max_rows = max(self_rows, other_rows)
        max_cols = max(self_cols, other_cols)

        new_grid = [[StreamTeX_Styles.none for _ in range(max_cols)] for _ in range(max_rows)]

        for i in range(self_rows):
            for j in range(len(self.css_grid[i])):
                new_grid[i][j] = self.css_grid[i][j]

        for i in range(other_rows):
            for j in range(len(other.css_grid[i])):
                if i < max_rows and j < max_cols:
                    new_grid[i][j] = combine_styles(new_grid[i][j], other.css_grid[i][j])

        return StyleGrid(new_grid)

    def _get_dimensions(self) -> Tuple[int, int]:
        if not self.css_grid:
            return 0, 0
        num_rows = len(self.css_grid)
        num_cols = max(len(row) for row in self.css_grid) if self.css_grid else 0
        return num_rows, num_cols

    @staticmethod
    def create(cells: str, style: Style, num_rows: Optional[int] = None, num_cols: Optional[int] = None):
        """Creates a StyleGrid with the specified cells filled with the given style."""
        from .base import StreamTeX_Styles
        cells_list = StyleGrid._parse_cells(cells)

        max_row_index = max((row for row, _ in cells_list), default=0)
        max_col_index = max((col for _, col in cells_list), default=0)

        grid_rows = max(num_rows if num_rows is not None else 0, max_row_index + 1)
        grid_cols = max(num_cols if num_cols is not None else 0, max_col_index + 1)

        grid = [[StreamTeX_Styles.none for _ in range(grid_cols)] for _ in range(grid_rows)]

        for row, col in cells_list:
            if row < grid_rows and col < grid_cols:
                grid[row][col] = style

        return StyleGrid(grid)

    @staticmethod
    def _parse_cells(cells_str: str) -> List[Tuple[int, int]]:
        """Parses a string of cell ranges in Excel-like notation."""
        cells = []
        ranges = cells_str.split(',')
        for cell_range in ranges:
            cell_range = cell_range.strip()
            if ':' in cell_range:
                start_cell, end_cell = cell_range.split(':')
                start_row, start_col = StyleGrid._cell_to_indices(start_cell.strip())
                end_row, end_col = StyleGrid._cell_to_indices(end_cell.strip())
                if start_row > end_row:
                    start_row, end_row = end_row, start_row
                if start_col > end_col:
                    start_col, end_col = end_col, start_col
                for row in range(start_row, end_row + 1):
                    for col in range(start_col, end_col + 1):
                        cells.append((row, col))
            else:
                row, col = StyleGrid._cell_to_indices(cell_range)
                cells.append((row, col))
        return cells

    @staticmethod
    def _cell_to_indices(cell: str) -> Tuple[int, int]:
        """Converts a cell reference (e.g., 'A1') to zero-based (row, col) indices."""
        match = re.match(r'^([A-Za-z]+)([0-9]+)$', cell)
        if not match:
            raise ValueError(f"Invalid cell reference: {cell}")
        col_str, row_str = match.groups()
        col_index = StyleGrid._column_letter_to_index(col_str)
        row_index = int(row_str) - 1
        return row_index, col_index

    @staticmethod
    def _column_letter_to_index(col_str: str) -> int:
        """Converts column letters to a zero-based column index."""
        col_str = col_str.upper()
        col_index = 0
        for char in col_str:
            if 'A' <= char <= 'Z':
                col_index = col_index * 26 + (ord(char) - ord('A') + 1)
            else:
                raise ValueError(f"Invalid column letter: {char}")
        return col_index - 1
