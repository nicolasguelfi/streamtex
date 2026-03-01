with st_grid(cols=3,
             cell_styles=(s.container.borders.solid_border
                          + s.center_txt)) as g:
    with g.cell():
        with st_block(s.container.paddings.tiny_padding
                      + s.container.bg_colors.dark_sea_green_bg):
            st_write("tiny (3pt)")
    with g.cell():
        with st_block(s.container.paddings.medium_padding
                      + s.container.bg_colors.dark_sea_green_bg):
            st_write("medium (12pt)")
    with g.cell():
        with st_block(s.container.paddings.large_padding
                      + s.container.bg_colors.dark_sea_green_bg):
            st_write("large (24pt)")
