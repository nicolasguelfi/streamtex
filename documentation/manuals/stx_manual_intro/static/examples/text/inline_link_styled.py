link_style = s.project.colors.primary_blue + s.text.decors.underline_text + s.large
theURL = "https://docs.streamlit.io"
st_write(link_style,
         "Styled link (no default decoration)",
         link=theURL, no_link_decor=True)
