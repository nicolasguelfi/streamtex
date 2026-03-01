picked = st.color_picker("Pick a text color", "#E74C3C",
                         key="bck25_color")
color_style = ns(f"color: {picked};")
with st_block(s.project.containers.result_box):
    st_write(color_style + s.Large + s.bold, "Colored text!")
