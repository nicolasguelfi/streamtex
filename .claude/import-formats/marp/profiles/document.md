# Profile: Document

> Faithful to the original Marp content. Full sentences, readable on screen/tablet.
> Designed as a course support document, not a projection deck.

## Target

- **Audience:** Self-study, course handout, reference material
- **Device:** Laptop, tablet, or printed PDF
- **Interaction:** Scroll or TOC navigation

## Typography

| Element | Size | Style reference |
|---|---|---|
| Block title | 48pt (Large) | `s.Large + s.bold + s.center_txt` |
| Section title | 32pt (large) | `s.large + s.bold + ColorsCustom.accent` |
| Body text | 24pt (big) | `s.big` |
| Keywords | 24pt bold + accent | `s.bold + ColorsCustom.accent + s.big` |
| Caption / source | 16pt (medium) | `s.medium + ColorsCustom.muted` |
| Code blocks | responsive | default `st_code()` |

## Content Rules

- **Preserve full text:** Keep complete sentences from Marp source
- **No condensation:** Do not shorten bullets or remove detail
- **Helper boxes:** USE `show_explanation()`, `show_details()`, `show_code()` for:
  - Learning objectives → `show_explanation()`
  - Detailed explanations → `show_details()`
  - Code examples → `show_code()`
- **Speaker notes:** Convert to `show_details()` (collapsible instructor notes)
- **Instructor slots:** Fully integrated via `show_explanation()` and `show_details()`
- **Tables:** Preserve full detail using `st_grid()` with all columns
- **Code:** Preserve complete code blocks, not just excerpts

## Layout

- **Grid:** Optional, use when source has image+text side-by-side
- **Responsive:** Same `repeat(auto-fit, minmax(350px, 1fr))` pattern
- **Images:** Integrated in flow, not forced to 50/50
- **Slide breaks:** NO `st_slide_break()` — use `st_br()` for light visual separation
- **Sections:** `st_space("v", 2)` between major sections

## book.py Configuration

```python
# No PresentationConfig — document mode
# set_presentation_config(...) → OMIT or comment out

st_book(
    [...],
    paginate=False,          # Continuous scroll
    banner=BannerConfig.hidden(),
    page_width=90,           # Narrower for readability
    zoom=100,
)

toc = TOCConfig(
    sidebar_max_level=3,
    numbering=NumberingMode.SIDEBAR_ONLY,
)
marker_config = MarkerConfig(auto_marker_on_toc=1)
```

## Theme

- **Base:** Configurable — dark or light
- **Dark default:** Same as slides profile
- **Light option:** Override in `.streamlit/config.toml`:
  ```toml
  [theme]
  base = "light"
  ```

## Slot Handling

- Default: fully integrated
- Learning Objectives → `show_explanation()` at top of block
- Context / Why → `show_explanation()` after title
- Core Content → main block body (full text)
- Hands-On → `show_details()` with activity instructions
- Key Takeaways → styled list at end of block
- References → `show_details()` with links

## custom/styles.py Differences

The document profile needs a separate `DocumentStylesCustom` class (or the same
`SlideStylesCustom` with smaller sizes). The step `02-theme-migrate.md` reads the
active profile to determine which sizes to generate.

```python
class DocumentStylesCustom:
    """Document-mode styles — optimized for screen reading."""
    headline = Style.create(
        ColorsCustom.primary + Text.weights.bold_weight + Text.sizes.Large_size
        + Text.alignments.center_align,
        "doc_headline"
    )
    body = Style.create(Text.sizes.big_size, "doc_body")
    keyword = Style.create(
        ColorsCustom.accent + Text.weights.bold_weight + Text.sizes.big_size,
        "doc_keyword"
    )
    question = Style.create(
        ColorsCustom.muted + Text.sizes.medium_size
        + Text.decors.italic_text + Text.alignments.center_align,
        "doc_question"
    )
```
