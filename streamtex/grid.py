import streamlit as st
from typing import List, Union
from contextlib import contextmanager
from .styles import Style, StyleGrid, StreamTeX_Styles
from .container import st_block
from .utils import generate_key
from .export import export_push_wrapper, export_pop_wrapper, is_export_active

# Helper type definition
CELL_STYLES_TYPE = Union[List[List[Style]], List[Style], Style, StyleGrid]

class GridController:
    def __init__(self, cols: str | int = 2, cell_styles: CELL_STYLES_TYPE = StreamTeX_Styles.none):
        self.cell_styles = cell_styles
        self.cell_counter = 0 # Tracks total cells to map styles to flat list/matrix
        
        # Infer column count
        if isinstance(cols, int):
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
        return StreamTeX_Styles.none

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
    grid_style: Style = StreamTeX_Styles.none, 
    cell_styles: CELL_STYLES_TYPE = StreamTeX_Styles.none,
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
    :param grid_style: A `Style` object applied to the entire grid. Defaults to `StreamTeX_Styles.none`.
    :param cell_styles: Styles for individual cells. Can be:
        - A `StyleGrid` object.
        - A matrix (list of lists) of `Style` objects.
        - A flat list of `Style` objects.
        - A single `Style` applied to all cells.
    
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
        with st_grid("auto 1fr") as g:
            # row 1, col 1 will only occupy as much as space as it needs
            with g.cell(): ...
            # row 1, col 2 will occupy the rest of the available space
            with g.cell(): ...
        ```
    """
    
    # 1. Generate ID
    grid_id = generate_key("css-grid")
    
    # 2. Convert int cols to str if needed
    template = cols
    if isinstance(cols, int):
        template = " ".join(["1fr"]*cols)
    
    
    # 3. Inject CSS
    # We target the direct parent stVerticalBlock of our marker.
    # We essentially turn the Streamlit Container into a CSS Grid Container.
    css = f"""
    <style>
        /* 1. Turn the container into a Grid */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) {{
            display: grid;
            grid-template-columns: {template};
            gap: 0;
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
        }}
        
        /* Apply Wrapper Style to the grid container itself if needed, 
           or we can wrap it. Here we apply to the grid container. */
        div[data-testid="stVerticalBlock"]:has(> .element-container .stHtml span.{grid_id}) {{
            {str(grid_style)}
        }}
    </style>
    """
    st.html(css)

    # 4. Export wrapper (no-op when export is inactive)
    if is_export_active():
        export_push_wrapper(
            f'<div style="display:grid;grid-template-columns:{template};gap:0;align-items:stretch;{grid_style}">')

    # 5. Render
    with st.container():
        # Marker
        st.html(f'<span class="{grid_id}" style="display:none"></span>')

        controller = GridController(cols, cell_styles)
        yield controller

    if is_export_active():
        export_pop_wrapper("</div>")