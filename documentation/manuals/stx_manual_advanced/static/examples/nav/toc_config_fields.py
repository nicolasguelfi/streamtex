toc = TOCConfig(
    numbering=NumberingMode.SIDEBAR_ONLY,  # numbers in sidebar only
    toc_position=0,
    title_style=s.project.titles.course_title + s.center_txt,
    content_style=s.large + s.text.colors.reset,
    sidebar_max_level=None,  # None = auto (paginated: 1, continuous: 2)
)
