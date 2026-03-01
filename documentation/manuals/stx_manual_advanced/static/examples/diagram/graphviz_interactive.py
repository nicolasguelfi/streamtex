DIAGRAMS = {
    "Simple Graph": "diagrams/simple_graph.dot",
    "StreamTeX Flowchart": "diagrams/flowchart.dot",
    "Architecture": "diagrams/architecture.dot",
    "Data Flow": "diagrams/data_flow.dot",
}

choice = st.selectbox("Choose a diagram", [*DIAGRAMS])
stx.st_graphviz(file=DIAGRAMS[choice])