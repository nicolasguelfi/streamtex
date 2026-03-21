# Template: presentation

StreamTeX presentation optimized for live projection at 10-20m distance.

## Defaults

| Setting | Value |
|---------|-------|
| Type | presentation |
| Audience | auditorium |
| Theme | dark |
| Pagination | yes |
| TOC | `NumberingMode.SIDEBAR_ONLY`, `sidebar_max_level=2` |
| Sidebar | `initial_sidebar_state="expanded"` |
| Banner | `BannerConfig.full()` |
| Marker | `MarkerConfig(auto_marker_on_toc=1, show_nav_ui=True)` — PageUp/PageDown |
| Body font | `s.Large` (48pt) — **mandatory minimum** |
| Title font | `s.Huge` (96pt) |
| Max blocks | 15 |

## Additional rules

**MANDATORY**: Read `.claude/designer/skills/slide-design-rules.md` for L1/L2/L3 grid system.

If `.claude/designer/presentation/skills/presentation-design-rules.md` exists,
also read it — it overrides base rules for live projection.

## Presentation-specific constraints

- **Body text**: `s.Large` (48pt) minimum — `s.large` (32pt) is too small for projection
- **Titles**: `s.Huge` (96pt) for main titles, `s.huge` (80pt) for section titles
- **Keywords only**: 5-7 words per bullet, max 3 bullets per section
- **No helper boxes**: `show_explanation()`, `show_details()`, `show_code()` are forbidden
- **High contrast**: Never use `muted`/`subtle` on body text
- **Generous spacing**: `st_space(size=4)` between major sections
- **Images**: minimum 400px width (except logos)
- **L1/L2/L3 grid**: Every slide uses the 3-row grid structure

## Default structure

| Position | Blueprint | Notes |
|----------|-----------|-------|
| First | 1 — Title | Course title (Huge), subtitle, author |
| Section starts | 2 — Section Header | Section number + title |
| Content slides | 3 — Text Content | L1 headline + L2 image/text grid |
| Comparison | 4 — Comparison | Side-by-side with responsive grid |
| Demo | 6 — Code + Result | Code with large font (20pt+) |
| Last | 10 — Conclusion | Key takeaways |

## BlockStyles pattern (presentation)

```python
class BlockStyles:
    """Simplified roles for projection."""
    heading = s.project.titles.section_title    # 80-96pt
    sub = s.project.titles.section_subtitle     # 48pt bold
    body = s.Large                              # 48pt
    body_accent = s.Large + s.project.colors.accent + s.bold
    keyword = s.bold + s.project.colors.accent  # Bold + accent for emphasis
    question = s.Large + s.italic               # L3 transition
    caption = s.large + s.project.colors.muted  # Sources/footers only
```

## book.py — Presentation Config Pattern

```python
from streamtex import (
    st_book, TOCConfig, MarkerConfig, ViewMode,
    set_presentation_config, PresentationConfig,
    set_slide_break_config, SlideBreakConfig, SlideBreakMode,
    PdfConfig, ExportConfig, ExportMode, PresentationProfile,
)

# Presentation configuration (fullscreen 16:9)
set_presentation_config(PresentationConfig(
    title="{{title}}",
    aspect_ratio="16/9",
    footer=True,
    center_content=True,
    hide_streamlit_header=True,
))

set_slide_break_config(SlideBreakConfig(
    mode=SlideBreakMode.HIDDEN,
    fullscreen=True,
    marker=True,
))

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
            filename="my-presentation",
            timestamp=True,
        ),
        ExportConfig(
            format="pdf",
            mode=ExportMode.NEVER,
            output_dir="./exports",
            filename="my-presentation",
            timestamp=True,
            pdf=PdfConfig(format="A4", landscape=True),
        ),
    ],
    # Display profiles: Presenter + Audience + Handout (phone icon in sidebar & floating bar)
    presentation_profiles=PresentationProfile.presentation_preset(),
)
```

## Block Naming Convention

Block files use **descriptive names** (e.g., `bck_title.py`, `bck_containers.py`, `bck_overview.py`),
never numeric prefixes (e.g., ~~`bck_01_title.py`~~). Order is defined in the `st_book([...])` call.

## Styles base

```python
# custom/styles.py — presentation template
class Styles(StxStyles):
    class project:
        class colors:
            primary = ns("color: #6C9AEF;", "pres_primary")
            accent = ns("color: #00d4ff;", "pres_accent")
            highlight = ns("color: #FFB547;", "pres_highlight")
            muted = ns("color: #94A3B8;", "pres_muted")

        class titles:
            course_title = s.Huge + s.bold + s.center_txt
            section_title = s.huge + s.bold + s.center_txt
            section_subtitle = s.Large + s.bold

        class containers:
            card = ns("background-color: rgba(255,255,255,0.05); border-radius: 12px; padding: 24px;", "pres_card")
            callout_highlight = ns("border-left: 4px solid #FFB547; background-color: rgba(255,183,71,0.1); padding: 16px;", "callout_hl")

        class slide:
            headline = s.huge + s.bold + s.center_txt
            body = s.Large
            question = s.Large + s.italic + s.center_txt
            keyword = s.bold + s.project.colors.accent
```
