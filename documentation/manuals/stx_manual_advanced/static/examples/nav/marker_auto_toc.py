from streamtex import MarkerConfig, st_book

# All TOC headings become markers
cfg = MarkerConfig(auto_marker_on_toc=True)

# Only levels 1 and 2 become markers
cfg = MarkerConfig(auto_marker_on_toc=2)

# Disabled (default) — no automatic bridge
cfg = MarkerConfig(auto_marker_on_toc=False)

st_book([...], marker_config=cfg)
