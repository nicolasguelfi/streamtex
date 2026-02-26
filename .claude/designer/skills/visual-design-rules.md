# Visual Design Rules for StreamTeX Slides

These rules apply to ALL block files in a StreamTeX presentation project.
They are the source of truth for visual quality.

## 1. Line Length & Readability

- **Max ~45 characters per visible line** on slides.
- Each `st_write()` creates a **separate HTML block** (new line).
- Use `st_br()` between `st_write()` calls for minimal breaks within a section.
- NEVER concatenate long text via multiple string args in one `st_write()`.

### WRONG
```python
st_write(s.large,
         "This is a very long line that will overflow the slide and look bad.")
```

### CORRECT
```python
st_write(s.large, "This is a short line")
st_br()
st_write(s.large, "that reads well on a slide.")
```

## 2. Multi-line Text Blocks

- Use `textwrap.dedent("""\...""")` for all helper text arguments.
- Applies to: `show_explanation()`, `show_details()`, `show_code()`.
- Each line in the dedented string becomes a separate rendered line.

```python
show_explanation(textwrap.dedent("""\
    Short first line for readability.
    Second line continues the explanation.
"""))
```

## 3. Font Size Hierarchy

| Level | Size | Usage |
|-------|------|-------|
| GIANT (196pt) | `s.GIANT` | Decorative only |
| huge (80pt) | `s.huge` | Course title |
| Large (48pt) | `s.Large` | Section title |
| large (32pt) | `s.large` | Body text, explanations |
| big (24pt) | `s.big` | Secondary text |
| medium (16pt) | `s.medium` | Small annotations |
| Code | Responsive (18pt) | `st_code()` via `--stx-code-size` variable |

- All body text in slides uses `s.large` (32pt).
- All label styles (explanation, details, tip, warning) use 32pt.
- Code blocks use the responsive CSS variable `--stx-code-size` (desktop 18pt, tablet 14pt, mobile 11pt).
- Use `wrap=True` for JSON/logs where alignment doesn't matter; keep `wrap=False` (default) for aligned code.

## 4. Canonical Section Structure

Every subsection follows this exact order:

```python
# 1. Subtitle with TOC registration
st_write(bs.sub, "Feature Name", toc_lvl="+1")
st_space("v", 1)

# 2. Explanation box (what & why)
show_explanation(textwrap.dedent("""\
    What this feature does.
    Why you would use it.
"""))
st_space("v", 1)

# 3. Code box (syntax-highlighted)
show_code(textwrap.dedent("""\
    st_write(s.large, "Example code")
"""))
st_space("v", 1)

# 4. Live rendering
st_write(s.large, "Example code")
st_space("v", 2)

# 5. Optional: details box (defaults & tips)
show_details(textwrap.dedent("""\
    Default: param=value.
    Additional tips about this feature.
"""))
```

## 5. Every Example Must Have Code

- **Every live rendering** must be preceded by a `show_code()` call.
- The code shown must match or represent the rendering below it.
- Only exceptions: headings, subtitles, spacers, helper calls.

## 6. WRONG/CORRECT Boxes

- Always explain **WHY** the WRONG code is wrong.
- Use `st_write()` + `st_br()` for the explanation, NOT concatenation.
- Then show the code with `show_code_inline()`.

```python
with st_block(s.project.containers.bad_callout):
    st_write(bs.wrong_label, "WRONG:")
    st_space("v", 1)
    st_write(s.large, "Explanation line 1.")
    st_br()
    st_write(s.large, "Explanation line 2.")
    st_space("v", 1)
    show_code_inline(textwrap.dedent("""\
        # the wrong code here
    """))
```

## 7. Default Parameter Values

- Always document defaults in `show_details()` sections.
- Format: `Default: param=value.`
- Key defaults to remember:
  - `st_write`: tag=Tags.span, toc_lvl=None, link="", hover=True
  - `st_grid`: cols=2, grid_style=none, cell_styles=none
  - `st_list`: list_type=lt.unordered, l_style=none, li_style=none
  - `st_image`: width="100%", height="auto"
  - `st_space`: direction="v", size="1em"
  - `st_code`: language="python", line_numbers=True, font_size="var(--stx-code-size, 18pt)", wrap=False

## 8. Block File Structure

```python
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
import textwrap


class BlockStyles:
    """Short description."""
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles


def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Title", tag=t.div, toc_lvl="1")
        st_space("v", 2)
        # ... sections follow canonical structure
```

## 9. Spacing

- `st_space("v", 2)` between major sections.
- `st_space("v", 1)` between elements within a section.
- `st_br()` for minimal breaks (e.g., between text lines).
- Separators between blocks handled by `st_book(separator=...)`.
