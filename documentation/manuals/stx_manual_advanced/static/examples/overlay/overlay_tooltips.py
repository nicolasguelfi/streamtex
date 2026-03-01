with st_overlay(s.container.sizes.width_full) as o:
    # Main content
    with st_block(s.container.bg_colors.light_blue_bg
                  + ns("height: 100px; padding: 20px;")):
        st_write(s.large, "Feature List")

    # Annotation arrows/labels
    with o.layer(top=30, right=10):
        st_write(ns("color: #FF6600; font-size: 12px;"),
                "← New feature")
