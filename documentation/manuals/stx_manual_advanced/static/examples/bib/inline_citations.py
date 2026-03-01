from streamtex.bib import cite
from custom.bib_refs import st_refs  # Generated — IDE completion!

# Option A: cite() with string keys
st_write(s.big,
    "The Transformer architecture ",
    cite("vaswani2017attention"),
    " revolutionized NLP."
)

# Option B: st_refs with IDE autocompletion (recommended)
st_write(s.big,
    "The Transformer architecture ",
    st_refs.vaswani2017attention,    # ← Ctrl+Space completes!
    " revolutionized NLP."
)

# For multi-key citations, use cite() directly:
cite("lecun2015deep", "goodfellow2016deep")  # (LeCun; Goodfellow)
