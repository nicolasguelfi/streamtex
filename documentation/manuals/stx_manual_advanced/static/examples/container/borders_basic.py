with st_grid(cols=3,
             cell_styles=(s.container.paddings.medium_padding
                          + s.center_txt + s.large)) as g:
    with g.cell():
        with st_block(s.container.borders.solid_border
                      + s.container.paddings.small_padding):
            st_write("solid")
    with g.cell():
        with st_block(s.container.borders.dashed_border
                      + s.container.paddings.small_padding):
            st_write("dashed")
    with g.cell():
        with st_block(s.container.borders.dotted_border
                      + s.container.paddings.small_padding):
            st_write("dotted")
    with g.cell():
        with st_block(s.container.borders.double_border
                      + s.container.borders.thick_border
                      + s.container.paddings.small_padding):
            st_write("double + thick")
    with g.cell():
        with st_block(s.container.borders.ridge_border
                      + s.container.borders.thick_border
                      + s.container.paddings.small_padding):
            st_write("ridge + thick")
    with g.cell():
        with st_block(s.container.borders.groove_border
                      + s.container.borders.thick_border
                      + s.container.paddings.small_padding):
            st_write("groove + thick")
