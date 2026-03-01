col1, col2 = st.columns(2)
show_a = col1.checkbox("Show block A", value=True,
                       key="bck30_show_a")
show_b = col2.checkbox("Show block B", key="bck30_show_b")

if show_a:
    with st_block(s.project.containers.good_callout):
        st_write(s.project.titles.tip_label,
                 "Block A")
        st_space("v", 1)
        st_write(s.large,
                 "Visible via Python conditional (if show_a).")
if show_b:
    with st_block(s.project.containers.tip_callout):
        st_write(s.project.titles.tip_label,
                 "Block B")
        st_space("v", 1)
        st_write(s.large,
                 "Visible via Python conditional (if show_b).")
if not show_a and not show_b:
    with st_block(s.project.containers.note_callout):
        st_write(s.large, "No blocks selected. Check a box above.")
