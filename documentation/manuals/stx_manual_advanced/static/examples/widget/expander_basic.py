with st.expander("Architecture Overview"):
    with st_block(s.project.containers.good_callout):
        st_write(s.project.titles.tip_label, "StreamTeX Architecture")
        st_space("v", 1)
        with st_list(list_type=lt.ordered, li_style=s.large) as l:
            with l.item():
                st_write("book.py orchestrates the app")
            with l.item():
                st_write("blocks/ contain the content modules")
            with l.item():
                st_write("custom/ holds project styles")

with st.expander("Style Examples"):
    with st_block(s.project.containers.note_callout):
        st_write(s.project.titles.details_label, "Composition")
        st_space("v", 1)
        st_write(s.large,
                 "Styles compose with + operator: s.bold + s.Large")
        st_br()
        st_write(s.large,
                 "Remove with - operator: style - s.bold")
