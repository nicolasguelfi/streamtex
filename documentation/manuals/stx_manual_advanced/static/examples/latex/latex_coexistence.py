# Mix StreamTeX text, math, and document rendering
st_write(s.Large, "Introduction to Linear Algebra")
stx.st_latex(r"\mathbf{A}\vec{x} = \vec{b}")
stx.st_latex_doc(r'''
    \section{Matrix Operations}
    Solving $\mathbf{A}\vec{x} = \vec{b}$ requires...
''', height=200)
