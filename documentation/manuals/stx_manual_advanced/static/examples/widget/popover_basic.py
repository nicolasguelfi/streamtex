with st.popover("Show info card"):
    with st_block(s.project.containers.result_box):
        st_write(s.large + s.bold + s.project.colors.primary_blue,
                 "StreamTeX Info")
        st_space("v", 1)
        st_write(s.large, "Version: 0.2.0")
        st_br()
        st_write(s.large, "Python >= 3.10")
        st_br()
        st_write(s.large, "Streamlit >= 1.54.0")
