# Block Blueprints — Template Catalog

This file documents 13 common block templates that Claude uses as reference
when generating code via `/stx-designer:update` (add block) or `/stx-designer:init`.

## How to use

> **Naming convention**: Block files use descriptive names (`bck_title.py`, `bck_containers.py`),
> never numeric prefixes. Order is defined in `st_book([...])`.

When the user requests a known block type, use the corresponding blueprint
as a base and adapt it to the context (topic, number of bullets,
color palette, target audience).

Blueprints define the **structure** (which `stx.*` calls, in which order),
not the exact content. Content is always adapted to the user's request.

> **MANDATORY CONVENTION**: Every block MUST contain at least one `st_write(...)` with `toc_lvl="1"` (or `toc_lvl="2"` for sub-sections within a larger block). This heading is required for the block to appear in the sidebar navigation and in the floating marker bar (`auto_marker_on_toc`). A block without any `toc_lvl` heading will be invisible in navigation. Even if the user does not request a title, always generate one that describes the block's purpose.

---

## Blueprint 1: Title (bck_title)

A title slide with course/project name, subtitle, author.

**When to use**: first slide of a presentation, project landing page.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_space("v", 4)
        st_write(bs.title, "Course Title", tag=t.div, toc_lvl="1")
        st_space("v", 2)
        st_write(bs.subtitle, "Descriptive subtitle", tag=t.div)
        st_space("v", 3)
        st_write(bs.author, "Author — Date", tag=t.div)
```

**Typical styles**:
- `title`: `s.huge + s.bold + s.center_txt`
- `subtitle`: `s.Large + s.center_txt`
- `author`: `s.large + s.center_txt + s.text.colors.muted`

---

## Blueprint 2: Section Header (bck_section)

A section introduction slide with number and title.

**When to use**: transition between major parts of a presentation.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_space("v", 3)
        st_write(bs.section_num, "Section N", tag=t.div)
        st_space("v", 1)
        st_write(bs.section_title, "Section Title", tag=t.div, toc_lvl="1")
        st_space("v", 2)
        st_write(bs.description, "Short description (1-2 lines)", tag=t.div)
```

**Typical styles**:
- `section_num`: `s.huge + s.bold + s.center_txt + s.text.colors.accent`
- `section_title`: `s.LARGE + s.center_txt`
- `description`: `s.large + s.center_txt + s.text.colors.muted`

---

## Blueprint 3: Text Content (bck_content)

A slide with title + bullets. The most common pattern.

**When to use**: explain a concept, list key points.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Topic Title", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.unordered) as l:
            with l.item(): st_write(bs.body, "First important point")
            with l.item(): st_write(bs.body, "Second point with detail")
            with l.item(): st_write(bs.body, "Third concise point")
```

**Typical styles**:
- `heading`: `s.huge + s.bold`
- `body`: `s.Large` (auditorium) or `s.large` (screen)

---

## Blueprint 4: Two-Column Comparison (bck_comparison)

A slide with 2 columns comparing concepts.

**When to use**: "X vs Y", pros/cons, before/after.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Concept A vs Concept B", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        with st_grid(cols="repeat(auto-fit, minmax(350px, 1fr))", gap="24px") as g:
            with g.cell():
                st_write(bs.col_title, "Concept A", tag=t.div)
                st_space("v", 1)
                with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.unordered) as l:
                    with l.item(): st_write(bs.body, "Point 1")
                    with l.item(): st_write(bs.body, "Point 2")
                    with l.item(): st_write(bs.body, "Point 3")
            with g.cell():
                st_write(bs.col_title, "Concept B", tag=t.div)
                st_space("v", 1)
                with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.unordered) as l:
                    with l.item(): st_write(bs.body, "Point 1")
                    with l.item(): st_write(bs.body, "Point 2")
                    with l.item(): st_write(bs.body, "Point 3")
```

**Typical styles**:
- `heading`: `s.huge + s.bold + s.center_txt`
- `col_title`: `s.Large + s.bold + s.text.colors.accent`
- `body`: `s.large`

---

## Blueprint 5: Image + Text (bck_image_text)

A slide with an image on the left and explanatory text on the right (or vice versa).

**When to use**: illustrate a concept with a diagram, schema, or photo.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Illustrated Title", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        with st_grid(cols="repeat(auto-fit, minmax(350px, 1fr))", gap="24px") as g:
            with g.cell():
                st_image(uri="static/images/illustration.png", width="100%")
            with g.cell():
                st_write(bs.body, "Explanatory text accompanying the image.")
                st_space("v", 1)
                with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.unordered) as l:
                    with l.item(): st_write(bs.body, "Detail 1")
                    with l.item(): st_write(bs.body, "Detail 2")
```

**Typical styles**:
- `heading`: `s.huge + s.bold`
- `body`: `s.large`

---

## Blueprint 6: Code + Result (bck_code_demo)

A slide showing source code and its result / output.

**When to use**: code demo, technical tutorial, syntax examples.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Demo: title", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        with st_grid(cols="repeat(auto-fit, minmax(350px, 1fr))", gap="24px") as g:
            with g.cell():
                st_code(
                    bs.code,
                    code="""\
                        # Source code
                        def hello():
                            print("Hello!")
                    """,
                    language="python",
                )
            with g.cell():
                with st_block(bs.result_box):
                    st_write(bs.body, "Result / output here")
```

**Typical styles**:
- `heading`: `s.huge + s.bold`
- `code`: default style (responsive)
- `result_box`: light accent background
- `body`: `s.large`

---

## Blueprint 7: Timeline / Steps (bck_timeline)

A slide with a sequence of numbered steps.

**When to use**: process, workflow, installation steps, methodology.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Process Steps", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        for i, (step_title, step_desc) in enumerate(steps, 1):
            with st_grid(cols="80px 1fr", gap="16px") as g:
                with g.cell():
                    st_write(bs.step_num, f"{i}.", tag=t.div)
                with g.cell():
                    st_write(bs.step_title, step_title, tag=t.div)
                    st_write(bs.step_desc, step_desc, tag=t.div)
            st_space("v", 1)
```

**Typical styles**:
- `heading`: `s.huge + s.bold`
- `step_num`: `s.LARGE + s.bold + s.text.colors.accent`
- `step_title`: `s.Large + s.bold`
- `step_desc`: `s.large + s.text.colors.muted`

---

## Blueprint 8: Quote / Highlight (bck_quote)

A slide with a quote or key message highlighted.

**When to use**: author quote, important message, intermediate conclusion.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_space("v", 3)
        with st_block(bs.quote_box):
            st_write(bs.quote_text, "The quote or key message here.", tag=t.div)
            st_space("v", 1)
            st_write(bs.attribution, "— Author, Source", tag=t.div)
        st_space("v", 3)
```

**Typical styles**:
- `quote_box`: accent background, generous padding, left border
- `quote_text`: `s.Huge + s.italic + s.center_txt`
- `attribution`: `s.Large + s.text.colors.muted + s.center_txt`

---

## Blueprint 9: Image Gallery (bck_gallery)

A slide with an image grid.

**When to use**: portfolio, visual examples, multiple screenshots.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Gallery", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        with st_grid(cols="repeat(auto-fit, minmax(200px, 1fr))", gap="16px") as g:
            with g.cell(): st_image(uri="static/images/img1.png")
            with g.cell(): st_image(uri="static/images/img2.png")
            with g.cell(): st_image(uri="static/images/img3.png")
```

**Typical styles**:
- `heading`: `s.huge + s.bold`

---

## Blueprint 10: Conclusion / Key Points (bck_conclusion)

A summary slide with the important points.

**When to use**: last slide, section summary, "key takeaways".

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Key Points", tag=t.div, toc_lvl="1")
        st_space("v", 2)
        with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.unordered) as l:
            with l.item(): st_write(bs.body, "Essential point 1")
            with l.item(): st_write(bs.body, "Essential point 2")
            with l.item(): st_write(bs.body, "Essential point 3")
        st_space("v", 3)
        st_write(bs.next_steps, "Next steps...", tag=t.div)
```

**Typical styles**:
- `heading`: `s.huge + s.bold + s.center_txt`
- `body`: `s.Large` (large text for impact)
- `next_steps`: `s.large + s.text.colors.muted + s.italic`

---

## Blueprint 11: AI-Generated Image + Text (bck_ai_image)

A slide with an AI-generated image and explanatory text.

**When to use**: the user wants an illustration but has no image file. Requires
`streamtex[ai]` and an `AIImageConfig` in book.py.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "AI-Illustrated Concept", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        with st_grid(cols="repeat(auto-fit, minmax(350px, 1fr))", gap="24px") as g:
            with g.cell():
                st_ai_image(
                    "A minimalist diagram of [topic], flat design, "
                    "dark background, blue and violet accents",
                    width="100%",
                    provider="openai",
                )
            with g.cell():
                st_write(bs.body, "Explanatory text alongside the AI image.")
                st_space("v", 1)
                with st_list(l_style=bs.body, li_style=bs.body, list_type=lt.unordered) as l:
                    with l.item(): st_write(bs.body, "Detail 1")
                    with l.item(): st_write(bs.body, "Detail 2")
```

**Typical styles**: same as Blueprint 5 (Image + Text).

**Prompt tips**: include style keywords (flat design, vector, dark bg, specific colors),
subject description, and composition guidance. Keep prompts under 200 characters.

---

## Blueprint 12: Interactive Image Lab (bck_image_lab)

A block with an interactive AI image generation widget.

**When to use**: hands-on demo, workshop, or when the end-user should
experiment with prompts.

**Structure**:
```python
def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Image Lab", tag=t.div, toc_lvl="2")
        st_space("v", 2)
        st_ai_image_widget(
            default_prompt="A serene mountain landscape at dawn",
            provider="openai",
            key="image_lab",
            show_save=True,
        )
```

**Note**: This blueprint uses Streamlit interactive widgets internally.
In manual mode (default), no API call is made until the user clicks Generate.
The widget is inherently interactive — the end-user can modify the prompt and
regenerate the image without any additional parameter.

---

## Blueprint 13: Fullscreen Slide (bck_fullscreen)

A fullscreen 16/9 slide with title, grid content, and generous spacing.

**When to use**: fullscreen presentation mode with `PresentationConfig`. Each slide
fills the viewport and is separated by `st_slide_break()`.

**Structure**:
```python
"""Fullscreen 16/9 slide with title, grid content, and generous spacing."""
from streamtex import *
from custom.styles import Styles as s

class BlockStyles:
    heading = s.Huge + s.bold + s.center_txt
    sub = s.Large + s.bold
    body = s.Large
    body_accent = s.Large + s.bold + s.text.colors.accent
    caption = s.large + s.muted
bs = BlockStyles

def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Slide Title", toc_lvl="1")
        st_space(size=3)
        with st_grid(cols="1fr 1fr", gap="32px"):
            st_image(uri="static/images/illustration.png", width="100%")
            with st_block():
                st_write(bs.sub, "Subtitle")
                st_space(size=2)
                with st_list(l_style=bs.body, li_style=bs.body) as l:
                    with l.item(): st_write(bs.body, "Key point 1")
                    with l.item(): st_write(bs.body, "Key point 2")
                    with l.item(): st_write(bs.body, "Key point 3")
        st_space(size=3)
        st_write(bs.caption, "Source: example.com")
    st_slide_break(marker_label="Slide Title")
```

**Typical styles**:
- `heading`: `s.Huge + s.bold + s.center_txt`
- `sub`: `s.Large + s.bold`
- `body`: `s.Large`
- `caption`: `s.large + s.muted`

**Note**: Use `paginate=False` with `PresentationConfig` in `book.py`. Each slide
ends with `st_slide_break()` for keyboard navigation (PageDown/PageUp).

---

## Quick reference

| User requests... | Blueprint |
|------------------|-----------|
| "title slide", "landing page" | 1 — Title |
| "section introduction", "transition" | 2 — Section Header |
| "slide with bullets", "explain X" | 3 — Text Content |
| "comparison X vs Y", "pros/cons" | 4 — Comparison |
| "image with text", "diagram + explanation" | 5 — Image + Text |
| "code demo", "syntax example" | 6 — Code + Result |
| "steps", "process", "workflow" | 7 — Timeline |
| "quote", "key message", "highlight" | 8 — Quote |
| "gallery", "portfolio", "screenshots" | 9 — Gallery |
| "conclusion", "summary", "key takeaways" | 10 — Conclusion |
| "AI image", "generate image", "image from prompt" | 11 — AI Image + Text |
| "image lab", "interactive generation", "prompt editor" | 12 — Interactive Image Lab |
| "fullscreen slide", "fullscreen presentation slide" | 13 — Fullscreen Slide |
