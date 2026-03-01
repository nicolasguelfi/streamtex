random.seed(0)
scatter_data = {
    "x": [random.gauss(0, 1) for _ in range(50)],
    "y": [random.gauss(0, 1) for _ in range(50)],
    "size": [random.uniform(10, 60) for _ in range(50)],
}
with st_block(s.project.containers.result_box):
    stx.st_scatter_chart(scatter_data, x="x", y="y", size="size")
