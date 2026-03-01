with st_block(s.container.bg_colors.dark_slate_gray_bg
              + s.container.paddings.medium_padding
              + s.center_txt):
    st_write(s.text.colors.white + s.Large, "Inside st_block")
    st_write(s.text.colors.light_gray + s.large,
             "Children stack vertically")