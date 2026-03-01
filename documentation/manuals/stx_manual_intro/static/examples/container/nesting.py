with st_block(bs.demo_border):
    st_write(s.bold + s.large, "Outer st_block")
    st_space("v", 1)
    with st_block(s.container.bg_colors.light_blue_bg
                  + s.container.paddings.small_padding):
        st_write(s.large,
                 "Inner st_block with light blue background")
        with st_span():
            st_write(s.large + s.bold, "Span child A  ")
            st_write(s.large + s.text.colors.coral,
                     "Span child B")
