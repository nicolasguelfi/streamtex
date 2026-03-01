with st_grid(cols=4, cell_styles=bs.cell) as g:
    with g.cell(): st_write(s.text.decors.italic_text + s.large, "italic")
    with g.cell(): st_write(s.text.decors.underline_text + s.large, "underline")
    with g.cell(): st_write(s.text.decors.strike_text + s.large, "strikethrough")
    with g.cell(): st_write(s.text.decors.decor_none_text + s.large, "none")
