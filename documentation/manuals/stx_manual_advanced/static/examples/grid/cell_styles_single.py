with st_grid(cols=2,
             cell_styles=bs.base_cell
                         + s.container.bg_colors.alice_blue_bg) as g:
    with g.cell(): st_write(s.large, "Same style")
    with g.cell(): st_write(s.large, "Same style")
    with g.cell(): st_write(s.large, "Same style")
    with g.cell(): st_write(s.large, "Same style")
