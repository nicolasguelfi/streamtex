from streamtex import st_grid, StyleGrid, Style as ns

# Create a grid with per-cell styling
# Cell (1,1) gets border, cell (2,2) gets background
cell_styles = StyleGrid()
cell_styles[(1, 1)] = ns("border: 2px solid #7AB8F5;")
cell_styles[(2, 2)] = ns("background: rgba(122, 184, 245, 0.1);")

with st_grid(cols="1fr 1fr", cell_styles=cell_styles):
    with g.cell(): st_write(s.large, "Top-left")
    with g.cell(): st_write(s.large, "Top-right (with border)")
    with g.cell(): st_write(s.large, "Bottom-left")
    with g.cell(): st_write(s.large, "Bottom-right (with bg)")
