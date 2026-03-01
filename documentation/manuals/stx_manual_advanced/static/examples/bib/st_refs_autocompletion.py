# Step 1: Generate typed module from your bibliography file
# Run once (or whenever your .bib changes):
#   uv run python -m streamtex generate-stubs static/refs.bib -o custom/bib_refs.py

# Step 2: Import st_refs from the generated module
from custom.bib_refs import st_refs  # ← IDE sees all keys!

st_write(s.big,
    "According to ", st_refs.vaswani2017attention,   # Ctrl+Space!
    " the Transformer architecture..."
)

# cite() still works for multi-key and prefix/suffix:
cite("lecun2015deep", "goodfellow2016deep")  # (LeCun; Goodfellow)
cite("vaswani2017attention", prefix="cf. ", suffix=", p. 42")
