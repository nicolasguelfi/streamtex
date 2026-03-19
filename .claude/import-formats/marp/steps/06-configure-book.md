# Step 6 — Configure book.py

> **Profile-aware:** Read the active profile from `.claude/import-formats/marp/profiles/{profile}.md`
> to determine pagination, presentation config, and layout defaults.

## Workflow

1. **Read** the active profile for book.py configuration
2. **Wire** all blocks in `st_book()` in chronological order
3. **Apply** profile-specific settings (see below)
4. **Apply** common settings
5. **Verify:** `python -c "import setup; import blocks"` (all blocks load)

## Profile-Specific Configuration

### slides profile

```python
set_presentation_config(PresentationConfig(
    title="Course Title",
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
    ...
)
```

### document profile

```python
# NO PresentationConfig — omit set_presentation_config() entirely

st_book(
    [...],
    paginate=False,              # continuous scroll
    banner=BannerConfig.hidden(),
    page_width=90,               # narrower for readability
    zoom=100,
    ...
)
```

## Common Configuration (both profiles)

```python
# Exports — MANUAL for sidebar buttons
exports=[
    ExportConfig(format="html", mode=ExportMode.MANUAL, ...),
    ExportConfig(format="pdf", mode=ExportMode.MANUAL, ...),
]

# TOC — show full hierarchy
toc = TOCConfig(
    sidebar_max_level=3,
    numbering=NumberingMode.SIDEBAR_ONLY,
    search=True,
)

# Markers — block roots only in floating nav
marker_config = MarkerConfig(
    auto_marker_on_toc=1,
    next_keys=["PageDown", "ArrowRight"],
    prev_keys=["PageUp", "ArrowLeft"],
    draggable=True,
    collapsible=True,
)

# Static sources — all st_image URIs are relative to this
stx.set_static_sources([str(Path(__file__).parent / "static")])
```

## Ordering Rules

Blocks are ordered in `book.py` following the course chronology:
1. Title block
2. Content blocks in day/session order
3. Conclusion block

## CRITICAL Reminders

- `ExportMode.MANUAL` (not `NEVER`) — otherwise no sidebar buttons
- Image URIs relative (no `static/` prefix)
- Update `page_title` in `st.set_page_config()` and `title` in `PresentationConfig`
