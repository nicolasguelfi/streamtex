from contextlib import contextmanager
from typing import List, Union

import streamlit as st

from .container import st_block
from .export import export_pop_wrapper, export_push_wrapper, is_export_active
from .styles import StxStyles, Style, StyleGrid
from .utils import generate_key

# Helper type definition
CELL_STYLES_TYPE = Union[List[List[Style]], List[Style], Style, StyleGrid]

# Default min-width lookup (based on ~900px Streamlit usable area)
_RESPONSIVE_MIN_WIDTHS: dict[int, int] = {
    1: 0, 2: 350, 3: 280, 4: 220, 5: 180, 6: 150,
}


def responsive_cols(cols: int, min_width: str | int | None = None) -> str:
    """Generate a responsive CSS grid-template-columns value.

    Args:
        cols: Target number of columns (>= 1).
        min_width: Minimum column width. Int is treated as px, str is used as-is.
                   If None, a sensible default is chosen based on ``cols``.

    Returns:
        A CSS ``grid-template-columns`` value using ``repeat(auto-fit, minmax(...))``.
    """
    if cols < 1:
        raise ValueError("responsive_cols requires cols >= 1")
    if cols == 1:
        return "1fr"
    if min_width is None:
        px = _RESPONSIVE_MIN_WIDTHS.get(cols, max(120, int(900 / cols)))
        min_width_str = f"{px}px"
    elif isinstance(min_width, int):
        min_width_str = f"{min_width}px"
    else:
        min_width_str = min_width
    return f"repeat(auto-fit, minmax({min_width_str}, 1fr))"


class GridController:
    def __init__(self, cols: str | int = 2, cell_styles: CELL_STYLES_TYPE = StxStyles.none,
                 intended_cols: int | None = None):
        self.cell_styles = cell_styles
        self.cell_counter = 0 # Tracks total cells to map styles to flat list/matrix

        # Infer column count
        if intended_cols is not None:
            self.cols = intended_cols
        elif isinstance(cols, int):
            self.cols = cols
        else:
            self.cols = cols.count(" ")+1

    def _resolve_style(self, idx: int) -> Style:
        """
        Determines the style for the current cell based on the global index.
        """
        styles = self.cell_styles

        # Case 1: Single Style
        if isinstance(styles, Style):
            return styles

        # Case 2: List of Styles (Flat)
        elif isinstance(styles, list):
            # Check if it is a Matrix (List of Lists)
            is_matrix = all(isinstance(row, list) for row in styles)
            if is_matrix:
                # Flatten the matrix for simple indexing
                flat_styles = [item for sublist in styles for item in sublist]
                if idx < len(flat_styles):
                    return flat_styles[idx]
            else:
                # Flat List
                if idx < len(styles):
                    return styles[idx]

        # Case 3: StyleGrid (Matrix object)
        elif isinstance(styles, StyleGrid):
            # Flatten logic for StyleGrid
            flat_grid = [item for sublist in styles.css_grid for item in sublist]
            if idx < len(flat_grid):
                return flat_grid[idx]

        # Case 4: Fallback
        return StxStyles.none

    @contextmanager
    def cell(self):
        """
        Yields a container that acts as a Grid Cell.
        """
        # 1. Resolve Style
        style_to_apply = self._resolve_style(self.cell_counter)
        self.cell_counter += 1

        # 2. Add 'height: 100%' so the background fills the grid cell vertically
        final_style = "height: 100%; width: 100%; box-sizing: border-box; " + str(style_to_apply)

        # 3. Render
        # We simply render a block. The Parent CSS Grid handles placement.
        with st_block(style=final_style):
            yield


@contextmanager
def st_grid(
    cols: str | int = 2,
    grid_style: Style = StxStyles.none,
    cell_styles: CELL_STYLES_TYPE = StxStyles.none,
    gap: str = None,
    responsive: bool = False,
    min_width: str | int | None = None,
    breakpoint: str | None = None,
):
    """
    A context manager representing a grid layout with customizable styles for the grid and individual cells.

    :param cols: The column layout, as either an int, or a CSS grid-template-columns string.
                    Examples:
                    - 2 (2 equal cols)
                    - "1fr 1fr 1fr" (3 equal cols)
                    - "auto 1fr" (First col fits content, second takes rest)
                    - "200px 1fr 200px" (Fixed sidebars)
                    - "repeat(auto-fill, minmax(200px, 1fr))" (Responsive card grid)
    :param grid_style: A `Style` object applied to the entire grid. Defaults to `StxStyles.none`.
    :param cell_styles: Styles for individual cells. Can be:
        - A `StyleGrid` object.
        - A matrix (list of lists) of `Style` objects.
        - A flat list of `Style` objects.
        - A single `Style` applied to all cells.
    :param responsive: When True and cols is an int, generates a responsive CSS template
                       using ``repeat(auto-fit, minmax(..., 1fr))``.
    :param min_width: Minimum column width for responsive mode. Int → px, str → as-is.
                      Providing this implicitly enables responsive mode when cols is an int.
    :param breakpoint: Viewport width below which the grid collapses to a single column.
                       Example: ``"600px"``. Injects a ``@media`` rule that overrides
                       ``grid-template-columns`` to ``1fr``.

    ## Notes:
    - Cells are filled from top to bottom, left to right.

    ## Usage Examples:
        ```
        with st_grid(2) as g:
            # row 1
            with g.cell(): ...
            with g.cell(): ...
            # row 2
            with g.cell(): ...
        ```

        ```
        with st_grid(cols=3, responsive=True) as g:
            # Responsive: wraps to fewer columns on narrow viewports
            with g.cell(): ...
            with g.cell(): ...
            with g.cell(): ...
        ```

        ```
        with st_grid(cols="25% 1fr", breakpoint="600px") as g:
            # 25/75 on desktop, single column on narrow screens
            with g.cell(): ...
            with g.cell(): ...
        ```
    """

    # 1. Generate ID
    grid_id = generate_key("css-grid")

    # If min_width is provided on an int cols, activate responsive implicitly
    if min_width is not None and isinstance(cols, int):
        responsive = True

    # Track intended column count for GridController
    intended_cols = cols if isinstance(cols, int) else None

    # 2. Convert cols to CSS template
    if responsive and isinstance(cols, int):
        template = responsive_cols(cols, min_width)
    elif isinstance(cols, int):
        template = " ".join(["1fr"]*cols)
    elif isinstance(cols, str) and not cols.strip():
        raise ValueError("st_grid cols parameter cannot be empty string")
    else:
        template = cols

    # 2b. Resolve gap value (explicit gap parameter takes priority over grid_style)
    gap_value = gap if gap else "0"


    # 3. Inject CSS
    # We target the direct parent stVerticalBlock of our marker.
    # We essentially turn the Streamlit Container into a CSS Grid Container.
    css = f"""
    <style>
        /* 1. Turn the container into a Grid */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) {{
            display: grid;
            grid-template-columns: {template};
            gap: {gap_value};
            align-items: stretch; /* Ensures equal height cells */
        }}

        /* 2. Hide Non-Cell Elements */
        /* Streamlit injects script tags and empty divs for st.html().
           We must force them to not take up grid slots. */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) > .element-container:has(style),
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) > .element-container:has(span.{grid_id}),
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) > .element-container:has(script) {{
            display: none !important;
        }}

        /* 3. Ensure Cells (stVerticalBlocks inside the grid) behave */
        /* The direct children of the grid are the 'cells'. */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) > .stVerticalBlock {{
            width: auto !important; /* Override Streamlit's width logic */
            min-width: 0; /* Prevent grid blowout from large images */
            overflow-wrap: break-word; /* Wrap long words inside cells */
            word-break: break-word; /* Fallback for older browsers */
        }}

        /* Apply Wrapper Style to the grid container itself if needed,
           or we can wrap it. Here we apply to the grid container. */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) {{
            {str(grid_style)}
        }}
        {"" if not breakpoint else f'''
        /* Container query: responds to actual content width, not viewport */
        .stMainBlockContainer {{
            container-type: inline-size;
        }}
        @container (max-width: {breakpoint}) {{
            div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) {{
                grid-template-columns: 1fr !important;
            }}
        }}
        '''}
    </style>
    """
    st.html(css)

    # 4. Export wrapper (no-op when export is inactive)
    if is_export_active():
        export_push_wrapper(
            f'<div style="display:grid;grid-template-columns:{template};gap:{gap_value};align-items:stretch;{grid_style}">')

    # 5. Render
    with st.container():
        # Marker
        st.html(f'<span class="{grid_id}" style="display:none"></span>')

        controller = GridController(template, cell_styles, intended_cols=intended_cols)
        yield controller

    if is_export_active():
        export_pop_wrapper("</div>")
