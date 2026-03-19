# Profile: Slides

> Optimized for live projection at 10-20m distance.
> Telegraphic content, large fonts, dark theme, paginated navigation.

## Target

- **Audience:** Live presentation in auditorium or meeting room
- **Device:** Projected screen (16:9)
- **Interaction:** PageDown/PageUp slide-by-slide

## Typography

| Element | Size | Style reference |
|---|---|---|
| Block title | 64pt | `s.project.slide.headline` |
| Section title | 58pt | `s.project.titles.section_title` |
| Body text | 48pt (Large) | `s.project.slide.body` |
| Keywords | 48pt bold + accent | `s.project.slide.keyword` |
| Caption / author | 32pt (large) | `s.project.slide.author` |
| Question / transition | 24pt (big) italic | `s.project.slide.question` |

## Content Rules

- **Condense text:** 3-7 words per bullet, max 5 bullets per list
- **Telegraphic style:** keywords, not full sentences
- **Bold keywords:** 1-2 highlighted words per bullet using `bs.keyword`
- **No helper boxes:** No `show_explanation()`, `show_details()`, `show_code()`
- **Speaker notes:** Omitted (or Python comments)
- **Instructor slots:** Skipped by default (`--no-slots`)

## Layout

- **Grid:** L1/L2/L3 structure from `slide-design-rules.md`
- **Responsive:** `repeat(auto-fit, minmax(350px, 1fr))`
- **Images:** Large, 50/50 grids with text
- **Slide breaks:** `st_slide_break()` between every slide (viewport spacer)

## book.py Configuration

```python
set_presentation_config(PresentationConfig(
    aspect_ratio="16/9",
    footer=True,
    center_content=False,
    enforce_ratio=False,
))

st_book(
    [...],
    paginate=True,
    banner=BannerConfig.hidden(),
    page_width=100,
    zoom=80,
)

toc = TOCConfig(sidebar_max_level=3)
marker_config = MarkerConfig(auto_marker_on_toc=1)
```

## Theme

- **Base:** Dark (`themes.py` with dark overrides)
- **Colors:** High contrast for projection
- **Never:** Hardcoded black/white

## Slot Handling

- Default: skip (`--no-slots`)
- If included: extract only slide-compatible content (titles, key bullets, images)
