with st_grid(cols=3, cell_styles=bs.cell) as g:
    with g.cell(): st_write(s.text.weights.bold_weight + s.large, "bold_weight")
    with g.cell(): st_write(s.text.weights.light_weight + s.large, "light_weight")
    with g.cell(): st_write(s.text.weights.normal_weight + s.large, "normal_weight")
