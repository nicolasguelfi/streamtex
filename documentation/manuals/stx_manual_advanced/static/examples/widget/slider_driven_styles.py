size = st.slider("Font size (px)", 12, 96, 32, key="bck25_slider")
dynamic_style = ns(f"font-size: {size}px;")
with st_block(s.project.containers.result_box):
    st_write(dynamic_style + s.bold, "Dynamic size text")
