with st_grid(cols=3, cell_styles=bs.cell) as g:
    with g.cell(): st_write(s.text.fonts.font_arial + s.large, "Arial")
    with g.cell(): st_write(s.text.fonts.font_georgia + s.large, "Georgia")
    with g.cell(): st_write(s.text.fonts.font_courier_new + s.large, "Courier New")
    with g.cell(): st_write(s.text.fonts.font_times_new_roman + s.large, "Times New Roman")
    with g.cell(): st_write(s.text.fonts.font_verdana + s.large, "Verdana")
    with g.cell(): st_write(s.text.fonts.font_monospace + s.large, "monospace")
