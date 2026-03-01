with st_grid(cols="1fr 2fr", cell_styles=bs.cell) as g:
    with g.cell(): st_write(s.large, "Narrow (1fr)")
    with g.cell(): st_write(s.large, "Wide (2fr)")