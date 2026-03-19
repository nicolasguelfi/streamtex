# HTML Import Conventions

> Reference document for HTML → StreamTeX conversion.
> Read this before any HTML import operation.

## 1. Source Analysis

### Filter CSS Noise

- **Ignore** class names (`c1`, `c12`, etc.) — focus on computed styles
- **Ignore** default black/white text — theme-controlled, not hardcoded
- **Ignore** default underlined links — keep browser default behavior
- **Focus on** bold, italic, colors, backgrounds, borders, font sizes

### Color Audit (MANDATORY)

For every HTML import, enumerate ALL non-default colors:
1. List every `color`, `background-color`, `border-color`, `text-decoration-color` value
2. Map each hex/rgb to a StreamTeX style name OR classify as "default — not migrated" with justification
3. Document in the `BlockStyles` class as a color-mapping summary comment

## 2. Style Mapping

| HTML Computed Style | StreamTeX |
|---|---|
| `font-weight: 700` | `s.bold` |
| `font-style: italic` | `s.italic` |
| `text-align: center` | `s.center_txt` |
| `color: #RRGGBB` | `ColorsCustom.name` in `custom/styles.py` |
| `background-color: #RRGGBB` | `BackgroundsCustom.name` |
| `font-size: Xpx` | Closest `Text.sizes.*` |

## 3. Component Mapping

| HTML Element | StreamTeX Component |
|---|---|
| `<table>` | `st_grid()` with `cell_styles` |
| `<ul>` / `<ol>` | `st_list()` with `l.item()` |
| `<br>` | `st_br()` |
| `<img>` | `st_image()` |
| `<a>` | Include font-size in link style when HTML shows text > 12pt |
| Inline mixed styles | ONE `st_write()` with tuples |

## 4. BlockStyles Class

Every converted block MUST have:

```python
class BlockStyles:
    """Topic description.

    Color mapping:
      #6C9AEF → primary (headings, links)
      #2ECC71 → accent (keywords, highlights)
      #E74C3C → warning (alerts, errors)

    Dropped colors:
      #000000 — default text, theme-controlled
      #FFFFFF — default background, theme-controlled
    """
    headline = s.project.pres.headline
    body = s.project.pres.body
    # ...
```

## 5. Family Detection

- Block name starts with `bckcp_` → use `s.project.doc.*` styles (document family)
- Block name starts with `bck_` → use `s.project.pres.*` styles (presentation family)

## 6. Image Naming

Rename images per convention:
```
[block_name]_image_[00index].[ext]
```

Copy to `static/images/` and reference with relative URIs (no `static/` prefix).

## 7. Verification Checklist

After conversion, verify:
- [ ] No raw HTML/CSS strings in Python code
- [ ] Semantic style names (not c1/c2)
- [ ] Images renamed per convention
- [ ] Lists use `st_list()` (not simulated bullets)
- [ ] Inline mixed-style text uses ONE `st_write()` with tuples
- [ ] Font sizes included on link styles where needed
- [ ] `st_br()` for line breaks
- [ ] `st_grid()` with `cell_styles` for tables
- [ ] No hardcoded black/white
- [ ] All non-default colors mapped
- [ ] Color-mapping summary in BlockStyles
- [ ] Dropped-colors log in BlockStyles
