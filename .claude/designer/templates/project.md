# Template: project

Standard StreamTeX project for screen viewing.

## Defaults

| Setting | Value |
|---------|-------|
| Type | presentation |
| Audience | screen |
| Theme | dark |
| Pagination | yes |
| TOC | `NumberingMode.SIDEBAR_ONLY`, `sidebar_max_level=2`, `search=True` |
| Sidebar | `initial_sidebar_state="expanded"` |
| Banner | `BannerConfig.full()` |
| Marker | `MarkerConfig(auto_marker_on_toc=1, show_nav_ui=True)` |
| Body font | `s.large` (32pt) |
| Title font | `s.huge` (80pt) |
| Max blocks | 15 |

## Default structure

| Position | Blueprint | Description |
|----------|-----------|-------------|
| First | 1 — Title | Project title, subtitle, author |
| Section start | 2 — Section Header | Section introduction |
| Content | 3 — Text Content | Main topic with bullets |
| Comparison | 4 — Two-Column Comparison | X vs Y |
| Illustration | 5 — Image + Text | Diagram with explanation |
| Technical demo | 6 — Code + Result | Code example with output |
| Process | 7 — Timeline | Step-by-step workflow |
| Key message | 8 — Quote | Highlighted quote or message |
| Visuals | 9 — Gallery | Image grid |
| Last | 10 — Conclusion | Key takeaways and next steps |

## Features

```python
# book.py configuration
from streamtex import (
    st_book, TOCConfig, NumberingMode, MarkerConfig, BannerConfig,
    PdfConfig, ExportConfig, ExportMode, PresentationProfile, ViewMode,
)

toc = TOCConfig(
    numbering=NumberingMode.SIDEBAR_ONLY,
    sidebar_max_level=2,
    search=True,
)
marker = MarkerConfig(auto_marker_on_toc=1, show_nav_ui=True)

st_book(
    module_list,
    toc_config=toc,
    marker_config=marker,
    paginate=True,
    banner=BannerConfig.full(),
    view_modes=[ViewMode.PAGINATED, ViewMode.CONTINUOUS],
    # Auto-export to disk (disabled by default — change NEVER to ALWAYS to enable)
    exports=[
        ExportConfig(
            format="html",
            mode=ExportMode.NEVER,
            output_dir="./exports",
            filename="my-project",
            timestamp=True,
        ),
        ExportConfig(
            format="pdf",
            mode=ExportMode.NEVER,
            output_dir="./exports",
            filename="my-project",
            timestamp=True,
            pdf=PdfConfig(format="A4", landscape=True),
        ),
    ],
    # Display profiles: Desktop + Mobile (phone icon in sidebar & floating bar)
    presentation_profiles=PresentationProfile.desktop_mobile_preset(),
)
```

## Styles base

```python
# custom/styles.py — project template defaults
class Styles(StxStyles):
    class project:
        class colors:
            primary = ns("color: #6C9AEF;", "primary")
            accent = ns("color: #00d4ff;", "accent")
            highlight = ns("color: #e94560;", "highlight")
            muted = ns("color: #8892b0;", "muted")

        class titles:
            course_title = s.Huge + s.bold + s.center_txt
            section_title = s.huge + s.bold + s.center_txt
            section_subtitle = s.Large + s.bold

        class containers:
            card = ns("background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 24px;", "card")
```

## Reference files

- `streamtex-docs/templates/template_project/` — rich template with 9 tutorial blocks
