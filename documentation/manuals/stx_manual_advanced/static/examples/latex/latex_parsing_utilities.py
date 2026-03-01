from streamtex import extract_tikz, extract_math, extract_frames

# Extract all TikZ diagrams
tikz_blocks = extract_tikz(latex_source)

# Extract all math formulas ($, $$, \[, \()
math_exprs = extract_math(latex_source)

# Extract all Beamer frames
frames = extract_frames(beamer_source)
