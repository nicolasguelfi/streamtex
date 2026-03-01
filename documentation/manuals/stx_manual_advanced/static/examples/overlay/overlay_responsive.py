with st_overlay(s.container.sizes.width_full) as o:
    with st_block(ns("height: 200px; background: #f0f0f0;")):
        st_write(s.large, "Container (responsive)")

    # Top-right corner (responsive to container size)
    with o.layer(top="10%", right="10%"):
        st_write(bs.overlay_text, "Responsive")

    # Center (responsive)
    with o.layer(top="50%", left="50%"):
        st_write(ns("color: red;"), "Centered")
