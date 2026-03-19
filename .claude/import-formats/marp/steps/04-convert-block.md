# Step 4 — Convert Blocks

> **Profile-aware:** Read the active profile from `.claude/import-formats/marp/profiles/{profile}.md`
> to determine content rules, font sizes, layout, and slide break behavior.

## CRITICAL RULE: Zero Residual Markdown

**Every Markdown element MUST be converted to its native `stx.*` component.**
No Markdown syntax may appear in strings passed to StreamTeX functions.

## Profile-Specific Behavior

### slides profile

- **Condense text:** 3-7 words/bullet, max 5 bullets
- **Telegraphic style:** keywords, not full sentences
- **Slide breaks:** `st_slide_break(marker_label="...")` BEFORE every slide (except first)
- **No helper boxes:** No `show_explanation()`, `show_details()`
- **BlockStyles:** Use `s.project.slide.*` (64pt headline, 48pt body)

### document profile

- **Preserve full text:** Keep complete sentences from source
- **No condensation:** All detail preserved
- **No slide breaks:** Use `st_br()` or `st_space("v", 2)` for separation
- **Helper boxes:** Use `show_explanation()`, `show_details()`, `show_code()`
- **BlockStyles:** Use `s.project.document.*` (48pt headline, 24pt body)
- **Speaker notes to `show_details()`:** Convert `<!-- notes -->` to collapsible boxes

## Conversion Table (common to both profiles)

| Marp Markdown | StreamTeX Native |
|---|---|
| `# Title` (first) | `st_write(bs.headline, "Title", toc_lvl="1")` |
| `## Section` | `st_write(bs.section, "Section", toc_lvl="+1")` |
| `## Slide` | `st_write(bs.headline, "Slide", toc_lvl="+2")` |
| `- item` | `st_list()` + `l.item()` |
| `**bold**` | `(bs.keyword, "text")` tuple |
| `![](img)` | `st_image(uri="images/...", width="100%")` |
| `![bg right:50%](img)` | `st_grid()` + `st_image()` |
| `> blockquote` | `st_block(s.project.containers.callout)` |
| `` ```code``` `` | `st_code(code="...", language="lang")` |
| `\|table\|` | `st_grid()` with cells |

## Forbidden Patterns (NEVER generate)

```python
st_write(bs.body, "- item")              # use st_list()
st_write(bs.body, "**bold**")            # use tuples
st.image("path")                          # use st_image()
st_write(bs.body, "* Item\n* Item")      # use st_list()
st_write(bs.headline, "X", toc_lvl="2")  # use "+1"
st_image(uri="static/images/...")         # no static/ prefix
```

## TOC Hierarchy (Relative — both profiles)

- `toc_lvl="1"` — ONE per block (absolute root)
- `toc_lvl="+1"` — Section or standalone slide
- `toc_lvl="+2"` — Slide under a section
- NEVER absolute `"2"`, `"3"` — always `"+N"`

## Slide Break Rules

### slides profile
```python
st_slide_break(marker_label="descriptive_snake_case")
st_write(bs.headline, "Slide Title", toc_lvl="+2")
```
NEVER remove slide breaks.

### document profile
```python
st_space("v", 2)
st_write(bs.headline, "Section Title", toc_lvl="+2")
```
NO `st_slide_break()` — continuous flow.

## Block File Template

```python
"""Block: [Topic]."""
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s


class BlockStyles:
    """[Topic]."""
    headline = s.project.slide.headline    # slides profile
    # headline = s.project.document.headline  # document profile
    body = s.project.slide.body
    keyword = s.project.slide.keyword
    question = s.project.slide.question
bs = BlockStyles


def build():
    st_write(bs.headline, "Block Title", toc_lvl="1")
    # ... profile-appropriate content ...
```
