data = _make_line_data()
with st_block(s.project.containers.result_box):
    stx.st_line_chart(data)
