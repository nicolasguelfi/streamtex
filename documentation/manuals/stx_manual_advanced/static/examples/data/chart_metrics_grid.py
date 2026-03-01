with st_grid(cols="1fr 2fr", cell_styles=bs.cell) as g:
    with g.cell():
        stx.st_metric("Users", "1,234", "+12%")
        stx.st_metric("Revenue", "$5.6K", "+8%")
        stx.st_metric("Uptime", "99.9%", "+0.1%")
    with g.cell():
        stx.st_line_chart(_make_line_data())
