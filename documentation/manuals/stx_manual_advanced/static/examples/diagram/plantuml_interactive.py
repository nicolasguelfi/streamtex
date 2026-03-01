DIAGRAMS = {
    "Class Diagram": "diagrams/class_diagram.puml",
    "Sequence Diagram": "diagrams/sequence_diagram.puml",
    "Use Case Diagram": "diagrams/usecase_diagram.puml",
}

choice = st.selectbox("Choose a PlantUML diagram", [*DIAGRAMS])
stx.st_plantuml(file=DIAGRAMS[choice], height=1000)