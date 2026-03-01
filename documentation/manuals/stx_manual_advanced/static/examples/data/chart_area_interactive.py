n_points = st.slider("Number of data points", 5, 100, 30,
                     key="bck27_area_slider")
with st_block(s.project.containers.result_box):
    stx.st_area_chart(_make_line_data(n_points))
