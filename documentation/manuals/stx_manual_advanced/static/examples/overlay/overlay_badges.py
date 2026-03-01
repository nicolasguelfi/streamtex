with st_overlay(s.container.sizes.width_full) as o:
    # Product card
    with st_block(s.container.bg_colors.light_gray_bg
                  + ns("height: 200px; width: 100%;")):
        st_write(s.large, "Product Image Area")

    # Sale badge (top-right)
    with o.layer(top=-10, right=-10):
        with st_block(ns("background: #FF4444; border-radius: 50%; "
                         "width: 60px; height: 60px; "
                         "display: flex; align-items: center;")):
            st_write(ns("color: white; text-align: center;"),
                    "SALE\n50%")
