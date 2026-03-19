# Import Conventions — Shared Rules for All Formats

> These rules apply to ALL import operations, regardless of the source format
> (Marp, HTML, LaTeX, etc.). Format-specific rules are in `.claude/import-formats/<format>/conventions.md`.

## 1. Zero Residual Markdown

**Every source element MUST be converted to a native `stx.*` component.**
No Markdown or HTML syntax may appear in strings passed to StreamTeX functions.

| Source syntax | StreamTeX native |
|---|---|
| `# Heading` | `st_write(style, "Heading", toc_lvl=...)` |
| `- item` / `* item` | `st_list()` + `l.item()` |
| `**bold**` | `(style, "text")` tuple in `st_write()` |
| `*italic*` | `(s.italic, "text")` tuple |
| `![](img)` | `st_image(uri="images/...", width="...")` |
| `> blockquote` | `st_block(container_style)` + `st_write()` |
| `` ```code``` `` | `st_code(code="...", language="...")` |
| `<table>` | `st_grid()` with cells |
| `<br>` | `st_br()` |

### Exception

Helper functions (`show_explanation()`, `show_details()`, `show_code()`) render via
`st_markdown()` internally — Markdown is allowed in their string arguments.

## 2. Image URI Rules

URIs are **always relative** to the static source configured in `book.py`:

```python
# book.py:
stx.set_static_sources([str(Path(__file__).parent / "static")])

# CORRECT — relative to static source
st_image(uri="images/photo.png", width="100%")

# WRONG — double prefix
st_image(uri="static/images/photo.png", width="100%")
```

### NEVER use:
- `st.image()` — always use `st_image()`
- Absolute paths
- URLs to local files
- `static/` prefix in URIs

## 3. TOC Levels (Relative Syntax)

| Syntax | Meaning | Resolves to |
|---|---|---|
| `toc_lvl="1"` | Block root (absolute anchor) | Level 1 |
| `toc_lvl="+1"` | One level below root | Level 2 |
| `toc_lvl="+2"` | Two levels below root | Level 3 |

### Rules

- **ONE** absolute `"1"` per block (the root title)
- **ALL** other headings use relative `"+N"` syntax
- **NEVER** use absolute `"2"`, `"3"`, etc.
- `+N` is relative to the last absolute level (`"1"`), NOT cumulative

## 4. BlockStyles Class (Mandatory)

Every imported block MUST define a `BlockStyles` class:

```python
class BlockStyles:
    """Topic description."""
    headline = s.project.slide.headline
    body = s.project.slide.body
    keyword = s.project.slide.keyword
bs = BlockStyles
```

## 5. Forbidden Patterns

These patterns must NEVER appear in generated code:

```python
# Markdown in st_write strings
st_write(bs.body, "- First point")        # use st_list()
st_write(bs.body, "**bold text**")         # use tuples
st_write(bs.body, "# Heading")            # use toc_lvl

# Wrong image function
st.image("path/to/image.png")             # use st_image()

# Simulated lists
st_write(bs.body, "* Item 1\n* Item 2")   # use st_list()

# Absolute toc levels (except root)
st_write(..., toc_lvl="2")                # use "+1"

# Static prefix in URIs
st_image(uri="static/images/file.png")    # remove "static/"
```

## 6. Style API Verification

When composing styles in `custom/styles.py`, use the correct API names:

| Category | Correct | WRONG |
|---|---|---|
| `Text.alignments` | `center_align` | `center_txt` |
| `Text.alignments` | `left_align` | `left_txt` |
| `Text.decors` | `italic_text` | `decorations.italic` |
| `Text.decors` | `underline_text` | `underline` |
| `Text` subclass | `decors` | `decorations` |

**Note:** `StxStyles` has `s.center_txt` as a convenience shortcut, but
`Text.alignments` does NOT. Use `Text.alignments.center_align` in compositions.

**Verification command:**
```bash
python -c "from streamtex.styles import Text; print(dir(Text.alignments))"
python -c "from streamtex.styles import Text; print(dir(Text.decors))"
```

## 7. Block File Template

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
    headline = s.project.slide.headline
    body = s.project.slide.body
    keyword = s.project.slide.keyword
bs = BlockStyles


def build():
    st_write(bs.headline, "Block Title", toc_lvl="1")
    # ... content ...
```

## 8. Adding a New Import Format

To add support for a new source format (e.g. LaTeX):

1. Create `commands/stx-import/latex.md` — the `/stx-import:latex` command
2. Create `import-formats/latex/conventions.md` — format-specific rules
3. Add `latex.md` to `stx-import` in `manifest.toml`
4. Add `latex = [...]` to `[import-formats]` in `manifest.toml`

The shared conventions (this file) and the `import-converter` agent are reused automatically.
