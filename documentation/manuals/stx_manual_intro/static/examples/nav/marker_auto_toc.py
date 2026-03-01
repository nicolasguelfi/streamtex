marker = MarkerConfig(
    auto_marker_on_toc=1,  # Level 1 headings become markers
    show_nav_ui=True
)
st_book([...], marker_config=marker)

# Exclude a heading from markers
st_write(s.huge, "Appendix", toc_lvl="1", marker=False)
