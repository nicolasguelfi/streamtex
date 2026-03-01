link_style = s.project.colors.primary_blue + s.text.decors.underline_text + s.large
theURL = "https://github.com"
st_write(s.large,
         "Visit the ",
         (s.project.colors.primary_blue + s.bold, "StreamTeX"),
         " project on ",
         (link_style, "GitHub", theURL))
