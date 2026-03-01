if "bck26_counter" not in st.session_state:
    st.session_state.bck26_counter = 0
if st.button("Increment", key="bck26_incr"):
    st.session_state.bck26_counter += 1
count = st.session_state.bck26_counter
size = min(12 + count * 4, 96)
with st_block(s.project.containers.result_box):
    st_write(ns(f"font-size: {size}px;") + s.bold,
             f"Count: {count}")
