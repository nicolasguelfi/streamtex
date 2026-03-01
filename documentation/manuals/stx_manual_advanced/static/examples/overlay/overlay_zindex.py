# Default: each layer on top of previous
with st_overlay(s.container.sizes.width_full) as o:
    # Base (z-index: auto)
    with st_block(...): pass

    # Layer 1 (z-index: auto, but defined later)
    with o.layer(top=20, left=20):
        st_write(..., "Layer 1")

    # To control explicitly:
    with o.layer(top=30, left=30):
        with st_block(ns("z-index: 10;")):
            st_write(..., "Higher z-index")
