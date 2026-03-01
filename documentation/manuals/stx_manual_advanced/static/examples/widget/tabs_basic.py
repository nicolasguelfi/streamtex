tab1, tab2, tab3 = st.tabs(["Text", "Grid", "List"])
with tab1:
    with st_block(s.project.containers.tip_callout):
        st_write(s.project.titles.tip_label, "Tip")
        st_space("v", 1)
        st_write(s.large, "Rich StreamTeX content inside a tab. "
                 "All stx.* functions work here.")
with tab2:
    with st_grid(cols=2, cell_styles=bs.cell) as g:
        with g.cell():
            st_write(s.large + s.bold, "Column A")
        with g.cell():
            st_write(s.large + s.bold, "Column B")
        with g.cell():
            st_write(s.large, "Data A1")
        with g.cell():
            st_write(s.large, "Data B1")
with tab3:
    with st_list(list_type=lt.unordered, li_style=s.large) as l:
        with l.item():
            st_write("First item in a tab")
        with l.item():
            st_write("Second item in a tab")
        with l.item():
            st_write("Third item in a tab")
