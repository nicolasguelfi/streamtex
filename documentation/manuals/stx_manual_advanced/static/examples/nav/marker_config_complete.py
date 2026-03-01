from streamtex import st_book, TOCConfig, MarkerConfig, BannerConfig

marker_config = MarkerConfig(
    auto_marker_on_toc=1,             # Level-1 TOC headings = markers
    nav_position="bottom-right",       # Widget in bottom-right corner
    next_keys=["PageDown", "ArrowRight"],
    prev_keys=["PageUp", "ArrowLeft"],
    nav_label_chars=40,                # Show up to 40 chars of label
)

st_book(
    [...],
    marker_config=marker_config,
    paginate=True,
    banner=BannerConfig.full(),        # Navigation banner style
)
