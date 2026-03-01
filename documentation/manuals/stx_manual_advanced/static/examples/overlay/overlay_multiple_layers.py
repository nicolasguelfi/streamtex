with st_overlay(s.container.sizes.width_full) as o:
    # Base layer
    with st_block(s.container.bg_colors.dark_blue_bg
                  + ns("height: 150px;")):
        st_write(s.text.colors.white, "Base Content")

    # Layer 1: Top-left
    with o.layer(top=10, left=10):
        st_write(bs.overlay_text, "Layer 1")

    # Layer 2: Top-right
    with o.layer(top=10, right=10):
        st_write(bs.overlay_text, "Layer 2")

    # Layer 3: Bottom-center
    with o.layer(bottom=10, left="50%"):
        st_write(bs.overlay_text, "Layer 3")
