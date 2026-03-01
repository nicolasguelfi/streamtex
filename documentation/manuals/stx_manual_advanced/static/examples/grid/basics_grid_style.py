table_style = ns("table-layout: fixed; width: 100%; border-collapse: collapse;")
with st_grid(cols=2, grid_style=table_style,
             cell_styles=bs.cell) as g:
    with g.cell(): st_write(s.bold + s.large, "Header A")
    with g.cell(): st_write(s.bold + s.large, "Header B")
    with g.cell(): st_write(s.large, "Data A1")
    with g.cell(): st_write(s.large, "Data B1")
