bar_data = _make_bar_data()
with st_block(s.project.containers.result_box):
    stx.st_bar_chart(bar_data, x="Category", y="Value")
