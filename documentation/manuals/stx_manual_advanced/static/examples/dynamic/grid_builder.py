c1, c2 = st.columns(2)
grid_cols = c1.slider("Columns", 1, 5, 3, key="bck30_cols")
grid_rows = c2.slider("Rows", 1, 4, 2, key="bck30_rows")

with st_grid(cols=grid_cols, cell_styles=bs.cell) as g:
    for i in range(grid_cols * grid_rows):
        with g.cell():
            st_write(s.large, f"Cell {i + 1}")
