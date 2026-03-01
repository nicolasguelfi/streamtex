with st_grid(cols=4,
             cell_styles=(s.container.paddings.medium_padding
                          + s.center_txt + s.large)) as g:
    with g.cell():
        with st_block(s.container.bg_colors.light_coral_bg
                      + s.container.paddings.small_padding):
            st_write("light_coral_bg")
    with g.cell():
        with st_block(s.container.bg_colors.light_blue_bg
                      + s.container.paddings.small_padding):
            st_write("light_blue_bg")
    with g.cell():
        with st_block(s.container.bg_colors.light_green_bg
                      + s.container.paddings.small_padding):
            st_write("light_green_bg")
    with g.cell():
        with st_block(s.container.bg_colors.light_golden_rod_yellow_bg
                      + s.container.paddings.small_padding):
            st_write("light_golden_rod_yellow_bg")
