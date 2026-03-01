header_style = (s.bold + s.large
                + s.container.bg_colors.steel_blue_bg
                + s.text.colors.white)
highlight = s.container.bg_colors.light_yellow_bg

with st_grid(
    cols=3,
    cell_styles=sg.create("A1:C1", header_style + bs.base_cell)
                + sg.create("A2:C3", s.large + bs.base_cell)
                + sg.create("B2", highlight + bs.base_cell)
) as g:
    # row 1 (header)
    with g.cell(): st_write("Name")
    with g.cell(): st_write("Role")
    with g.cell(): st_write("Status")
    # row 2
    with g.cell(): st_write("Alice")
    with g.cell(): st_write("Developer (highlighted)")
    with g.cell(): st_write("Active")
    # row 3
    with g.cell(): st_write("Bob")
    with g.cell(): st_write("Designer")
    with g.cell(): st_write("Active")
