with st_grid(cols=3, cell_styles=bs.cell) as g:
    with g.cell(): st_write(s.large, "Cell A1")
    with g.cell(): st_write(s.large, "Cell B1")
    with g.cell(): st_write(s.large, "Cell C1")
    with g.cell(): st_write(s.large, "Cell A2")
    with g.cell(): st_write(s.large, "Cell B2")
    with g.cell(): st_write(s.large, "Cell C2")
