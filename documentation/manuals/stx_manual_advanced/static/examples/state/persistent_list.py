if "bck26_items" not in st.session_state:
    st.session_state.bck26_items = []
with st.form("bck26_add_item_form"):
    new_item = st.text_input("New item")
    added = st.form_submit_button("Add to list")
if added and new_item:
    st.session_state.bck26_items.append(new_item)
if st.session_state.bck26_items:
    with st_block(s.project.containers.result_box):
        with st_list(list_type=lt.ordered, li_style=s.large) as l:
            for item in st.session_state.bck26_items:
                with l.item():
                    st_write(item)
