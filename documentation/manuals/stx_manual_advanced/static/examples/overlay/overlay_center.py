with st_overlay(s.container.sizes.width_full) as o:
    with st_block(s.container.bg_colors.light_blue_bg
                  + ns("height: 200px; width: 100%;")):
        st_write(s.large, "Background")

    # Center overlay
    with o.layer(top="50%", left="50%"):
        with st_block(ns("transform: translate(-50%, -50%);")):
            st_write(bs.overlay_text, "Centered")
