STYLE_PRESETS = {
    "Bold Blue": s.bold + s.Large + s.project.colors.primary_blue,
    "Italic Teal": s.italic + s.Large + s.project.colors.accent_teal,
    "Warning Red": s.bold + s.Large + s.project.colors.warning_red,
    "Success Green": s.bold + s.Large + s.project.colors.success_green,
    "Amber Highlight": s.bold + s.Large + s.project.colors.highlight_amber,
}

choice = st.selectbox("Choose a style preset",
                      [*STYLE_PRESETS],
                      key="bck30_style_select")
with st_block(s.project.containers.result_box):
    st_write(STYLE_PRESETS[choice],
             "Sample text with the selected style")
