user_text = st.text_input("Type something", key="bck25_text",
                          value="Hello StreamTeX")
if user_text:
    with st_block(s.project.containers.result_box):
        st_write(s.large + s.italic, user_text)
        st_br()
        st_write(s.large + s.bold + s.project.colors.primary_blue,
                 user_text)
        st_br()
        st_write(s.large + s.text.decors.underline_text
                 + s.project.colors.accent_teal, user_text)
