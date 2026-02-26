# StreamTeX Quick Reference for Presentation Designers

Condensed API reference. For full details, see `documentation/streamtex_cheatsheet_en.md`.

## Essential Imports (every block file)

```python
import streamlit as st
from streamtex import *
import streamtex as stx
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt
from custom.styles import Styles as s
from blocks.helpers import show_code, show_explanation, show_details
```

## Block File Structure

```python
class BlockStyles:
    heading = s.project.titles.section_title + s.center_txt
    sub = s.project.titles.section_subtitle
bs = BlockStyles

def build():
    with st_block(s.center_txt):
        st_write(bs.heading, "Title", tag=t.div, toc_lvl="1")
        st_space("v", 2)
        # content here...
```

## Text Rendering — `st_write()`

```python
# Simple text
st_write(s.large, "Hello world")

# Inline mixed styles (ONE call with tuples)
st_write(s.large,
         "Normal ", (s.bold, "bold"), " and ",
         (s.italic + s.project.colors.primary, "styled"), " text.")

# With link
st_write(s.large, "See ", (s.project.colors.primary + s.large, "docs", "https://..."), ".")

# TOC registration
st_write(bs.heading, "Section Title", tag=t.div, toc_lvl="1")
st_write(bs.sub, "Subsection", toc_lvl="+1")
```

## Containers

```python
# Vertical stacking container
with st_block(style):
    st_write(s.large, "Inside a block")

# Horizontal inline container
with st_span(style):
    st_write(s.large, "Inline content")
```

## Grid Layout — `st_grid()`

```python
# Equal columns
with st_grid(cols=3) as g:
    with g.cell(): st_write(s.large, "Col 1")
    with g.cell(): st_write(s.large, "Col 2")
    with g.cell(): st_write(s.large, "Col 3")

# CSS template columns
with st_grid(cols="1fr 2fr") as g:
    with g.cell(): st_write(s.large, "Narrow")
    with g.cell(): st_write(s.large, "Wide")

# Per-cell styling with StyleGrid
styled = (
    sg.create("A1:B1", s.bold + s.container.bg_colors.blue_bg)  # header row
    * sg.create("A1:A3", s.text.colors.white)                    # first column
)
with st_grid(cols=2, cell_styles=styled) as g:
    # cells...
```

## Lists — `st_list()`

```python
with st_list(list_type=lt.unordered, li_style=s.large) as l:
    with l.item(): st_write("Item A")
    with l.item():
        st_write("Item B")
        with st_list(li_style=s.medium) as l2:  # nested
            with l2.item(): st_write("Sub-item B.1")

with st_list(list_type=lt.ordered) as l:
    with l.item(): st_write("First")
    with l.item(): st_write("Second")
```

## Images — `st_image()`

```python
st_image(uri="static/images/photo.png", width="400px", height="auto", alt="Description")

# Clickable image
st_image(uri="static/images/logo.png", link="https://...", hover=True)
```

## Code Blocks — `st_code()`

```python
# Basic code block (responsive font size: desktop 18pt, tablet 14pt, mobile 11pt)
st_code(style, code="print('hello')", language="python", line_numbers=True)

# With line wrapping (useful for JSON, logs, prose-like code)
st_code(style, code='{"key": "long value..."}', language="json", wrap=True)

# Custom font size (overrides responsive default)
st_code(style, code="print('hello')", font_size="14pt")
```

## Spacing

```python
st_space("v", 2)          # Vertical space (2em) — between major sections
st_space("v", 1)          # Vertical space (1em) — between elements
st_space("h", "20px")     # Horizontal space
st_br()                   # Minimal line break
```

## Overlays — `st_overlay()`

```python
with st_overlay() as o:
    st_image(uri="background.png", width="800px", height="300px")
    with o.layer(top=120, left=250):
        st_write(s.bold + s.Large, "Overlaid text")
```

## Block Inclusion — `st_include()`

```python
# Embed another block inside the current one
st_include(block_file_module=blocks.sub_block)
```

## Style System

```python
# Built-in styles: s.bold, s.italic, s.large, s.Large, s.huge, s.center_txt, ...

# Compose with +
title = s.bold + s.Large + s.project.colors.primary

# Remove with -
no_bold = title - s.bold

# One-off CSS
custom = ns("border-left: 4px solid blue; padding: 8px;")

# Named themed style (supports dark mode)
named = Style.create(s.bold + s.Large, "my_title")

# Project palette: s.project.colors.*, s.project.titles.*, s.project.containers.*
```

## Helpers (from `blocks/helpers.py`)

```python
show_explanation("What this does and why.")   # Blue callout
show_code("st_write(s.bold, 'Hello')")        # Syntax-highlighted code
show_details("Default: tag=Tags.span.")       # Amber callout
show_code_inline("inline code")               # Code without wrapper box
```

## Book Orchestration (`book.py`)

```python
from streamtex import st_book, TOCConfig, MarkerConfig, BannerConfig

toc = TOCConfig(numerate_titles=False, toc_position=0)
marker = MarkerConfig(auto_marker_on_toc=1, show_nav_ui=True)

st_book([blocks.bck_01, blocks.bck_02, ...],
        toc_config=toc, marker_config=marker, paginate=True,
        banner=BannerConfig.full())
```

### Banner Presets

```python
banner=BannerConfig.full()           # Default — prominent, with dividers
banner=BannerConfig.compact()        # Slim, no dividers
banner=BannerConfig.compact_gray()   # Compact with neutral gray
banner=BannerConfig.hidden()         # No visual, navigation preserved
```

## Export-Aware Widgets

Always use `stx.*` instead of `st.*` for widgets that should survive HTML export:

| Streamlit | StreamTeX (export-aware) |
|-----------|------------------------|
| `st.dataframe()` | `stx.st_dataframe()` |
| `st.table()` | `stx.st_table()` |
| `st.metric()` | `stx.st_metric()` |
| `st.json()` | `stx.st_json()` |
| `st.line_chart()` | `stx.st_line_chart()` |
| `st.bar_chart()` | `stx.st_bar_chart()` |
| `st.area_chart()` | `stx.st_area_chart()` |
| `st.scatter_chart()` | `stx.st_scatter_chart()` |
| `st.graphviz_chart()` | `stx.st_graphviz()` |
| `st.audio()` | `stx.st_audio()` |
| `st.video()` | `stx.st_video()` |

## Collections (`book.py` for a hub)

```python
from streamtex import st_collection, CollectionConfig

config = CollectionConfig.from_toml("collection.toml")
st_collection(config=config, home_styles=s)
```

## Block Registries (automatic in `blocks/__init__.py`)

- **ProjectBlockRegistry**: Lazy-loads `bck_*.py` from the project's `blocks/` folder. Zero config.
- **LazyBlockRegistry**: Loads blocks from external paths (shared blocks, cross-project reuse).

```python
# In book.py for shared blocks:
shared = stx.LazyBlockRegistry([Path("../shared-blocks/blocks")])
st_book([blocks.bck_01, shared.bck_footer], ...)
```
