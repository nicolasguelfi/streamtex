DIAGRAMS = {
    "Function Plot": "diagrams/simple_shapes.tex",
    "Neural Network": "diagrams/neural_network.tex",
    "Finite Automaton": "diagrams/finite_automaton.tex",
}
PREAMBLES = {"Finite Automaton": r"\usetikzlibrary{automata,positioning}"}

choice = st.selectbox("Choose a TikZ diagram", [*DIAGRAMS])
stx.st_tikz(file=DIAGRAMS[choice], height=800, preamble=PREAMBLES.get(choice, ""))