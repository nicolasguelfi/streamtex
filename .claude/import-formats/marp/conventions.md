# Migration Coding Conventions

> Reference document for Marp → StreamTeX migration.
> All conversion commands and agents MUST follow these rules.
> Every step MUST read the active profile before proceeding.

## 0. Profiles

Two import profiles are available in `.claude/import-formats/marp/profiles/`:

| Profile | Use case | Fonts | Content | Pagination | Slide breaks |
|---|---|---|---|---|---|
| `slides` | Projection | 48pt+ body | Telegraphic, condensed | `paginate=True` | `st_slide_break()` |
| `document` | Screen/tablet reading | 24pt body | Full sentences | `paginate=False` | `st_br()` only |

Every step reads the active profile to determine behavior.
The profile is set via `--profile slides|document` on `/stx-import:marp`.

## 1. Image URIs

URIs are relative to the static source configured in `book.py` via `set_static_sources()`.

```python
# book.py configures:
stx.set_static_sources([str(Path(__file__).parent / "static")])

# CORRECT — relative to static source
st_image(uri="images/day1/file.png", width="100%")

# WRONG — double prefix, image will NOT resolve
st_image(uri="static/images/day1/file.png", width="100%")
```

Images are organized by day: `static/images/day{N}/filename.png`.

## 2. TOC Levels (Relative)

Use StreamTeX's native relative `toc_lvl` syntax.

| Syntax | Meaning | Resolves to |
|---|---|---|
| `toc_lvl="1"` | Block root (absolute anchor) | Level 1 |
| `toc_lvl="+1"` | Section or standalone slide | Level 2 |
| `toc_lvl="+2"` | Slide under a section | Level 3 |
| `toc_lvl="+3"` | Sub-heading in a slide | Level 4 |

### Rules

- ONE absolute `"1"` per block (the root title)
- All other headings use relative `"+N"` syntax
- NEVER use absolute `"2"`, `"3"`, etc.
- Section title slides (centered, `slide_title` style) → `"+1"`
- Content slides under a section → `"+2"`
- Standalone slides (takeaways, questions) → `"+1"`

### How relative resolution works

`+N` is relative to the last **absolute** level set (`"1"`), NOT cumulative.
Multiple `"+1"` in sequence all resolve to level 2 (not 2, 3, 4...).

```python
st_write(..., toc_lvl="1")    # → level 1  (sets current_level = 1)
st_write(..., toc_lvl="+1")   # → level 2  (1 + 1, current_level stays 1)
st_write(..., toc_lvl="+1")   # → level 2  (1 + 1, same)
st_write(..., toc_lvl="+2")   # → level 3  (1 + 2, current_level stays 1)
st_write(..., toc_lvl="+2")   # → level 3  (1 + 2, same)
```

## 3. Slide Breaks

**Mandatory** between every slide (except before the first).

```python
st_slide_break(marker_label="descriptive_snake_case")
st_write(bs.headline, "Slide Title", toc_lvl="+2")
```

- `marker_label` must be descriptive and snake_case
- Slide breaks create hidden markers for PageDown/PageUp navigation
- Slide breaks create viewport-height spacers for visual separation
- NEVER remove slide breaks — they are navigation waypoints

## 4. Style API Names

**CRITICAL:** The StreamTeX style API has specific attribute names.

| Category | Correct | WRONG |
|---|---|---|
| `Text.alignments` | `center_align` | `center_txt` |
| `Text.alignments` | `left_align` | `left_txt` |
| `Text.alignments` | `right_align` | `right_txt` |
| `Text.decors` | `italic_text` | `decorations.italic` |
| `Text.decors` | `underline_text` | `underline` |
| `Text` subclass | `decors` | `decorations` |

**Note:** `StxStyles` has `s.center_txt` as a convenience shortcut,
but `Text.alignments` does NOT. When composing in `custom/styles.py`,
use `Text.alignments.center_align`.

**Verification:**
```bash
python -c "from streamtex.styles import Text; print(dir(Text.alignments))"
python -c "from streamtex.styles import Text; print(dir(Text.decors))"
```

## 5. Export Config

| Mode | Behavior |
|---|---|
| `ExportMode.MANUAL` | Sidebar buttons visible, export on demand |
| `ExportMode.ALWAYS` | Auto-export after every render |
| `ExportMode.NEVER` | No buttons, export disabled |

**Default for new projects:** `MANUAL` (not `NEVER`).

## 6. book.py Defaults

```python
# TOC — show full hierarchy
sidebar_max_level=3

# Markers — block roots only in floating nav
auto_marker_on_toc=1

# Exports — sidebar buttons enabled
mode=ExportMode.MANUAL
```

## 7. Block Structure Summary

```python
def build():
    # Root (absolute "1")
    st_write(bs.headline, "Block Title", toc_lvl="1")

    st_slide_break(marker_label="section")
    # Section (relative "+1" → level 2)
    st_write(s.project.titles.slide_title, "Section", toc_lvl="+1")

    st_slide_break(marker_label="slide")
    # Slide under section (relative "+2" → level 3)
    st_write(bs.headline, "Slide", toc_lvl="+2")

    st_slide_break(marker_label="standalone")
    # Standalone slide (relative "+1" → level 2)
    st_write(bs.headline, "Takeaways", toc_lvl="+1")
```
