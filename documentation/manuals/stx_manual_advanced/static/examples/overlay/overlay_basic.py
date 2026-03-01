with st_overlay(s.container.sizes.width_full) as o:
    with st_block(s.container.bg_colors.dark_slate_blue_bg
                  + ns("height: 200px; width: 100%;")):
        st_write(s.text.colors.white + s.large,
                 "Base content area (dark background)")
    with o.layer(top=20, left=20):
        with st_block(bs.overlay_bg):
            st_write(bs.overlay_text, "Top-Left")
    with o.layer(bottom=20, right=20):
        with st_block(bs.overlay_bg):
            st_write(bs.overlay_text, "Bottom-Right")
