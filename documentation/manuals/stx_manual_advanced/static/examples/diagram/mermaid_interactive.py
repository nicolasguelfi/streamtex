DIAGRAMS = {
    "Flowchart": "diagrams/flowchart.mmd",
    "Sequence Diagram": "diagrams/sequence.mmd",
    "Class Diagram": "diagrams/class_diagram.mmd",
}

choice = st.selectbox("Choose a Mermaid diagram", [*DIAGRAMS])
stx.st_mermaid(file=DIAGRAMS[choice], height=1000)