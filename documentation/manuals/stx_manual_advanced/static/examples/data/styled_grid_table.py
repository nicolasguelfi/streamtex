header_style = sg.create("A1:C1", bs.header_cell)
data_style = sg.create("A2:C5", bs.data_cell)
with st_grid(cols=3, cell_styles=header_style + data_style) as g:
    for col in ["Name", "Role", "Score"]:
        with g.cell(): st_write(col)
    for i in range(len(data["Name"])):
        for col in ["Name", "Role", "Score"]:
            with g.cell(): st_write(str(data[col][i]))
