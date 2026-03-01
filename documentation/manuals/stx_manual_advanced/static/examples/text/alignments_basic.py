cell_wide = bs.cell + s.container.sizes.width_full
with st_block(cell_wide):
    st_write(s.text.alignments.left_align + s.large,
             "left_align", tag=t.div)
with st_block(cell_wide):
    st_write(s.text.alignments.center_align + s.large,
             "center_align", tag=t.div)
with st_block(cell_wide):
    st_write(s.text.alignments.right_align + s.large,
             "right_align", tag=t.div)
with st_block(cell_wide):
    st_write(s.text.alignments.justify_align + s.large,
             "justify_align spreads text evenly across the full width",
             tag=t.div)
