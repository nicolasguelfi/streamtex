if st.button("Say hello", key="bck25_hello"):
    with st_block(s.project.containers.result_box):
        st_write(s.large + s.bold + s.project.colors.success_green,
                 "Hello from StreamTeX!")
show = st.toggle("Show styled block", key="bck25_toggle")
if show:
    with st_block(s.project.containers.tip_callout):
        st_write(s.large, "This block appears when toggled on.")
