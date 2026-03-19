# Step 2 — Migrate Theme

> **Profile-aware:** Read the active profile from `.claude/import-formats/marp/profiles/{profile}.md`
> to determine font sizes, style class names, and theme defaults.

## Workflow

1. **Read** the active profile — determines font sizes and style structure
2. **Read** the source Marp CSS theme file
3. **Extract** CSS variables and key selectors
4. **Verify** StreamTeX style API attribute names (see below)
5. **Generate** `custom/styles.py`:
   - `ColorsCustom` — extracted from CSS variables
   - `BackgroundsCustom` — extracted from section backgrounds
   - `TextStylesCustom` — title hierarchy
   - `ContainerStylesCustom` — callout, grid presets, gaps
   - **slides profile:** `SlideStylesCustom` — 64pt headline, 48pt body
   - **document profile:** `DocumentStylesCustom` — 48pt headline, 24pt body
6. **Generate** `custom/themes.py` — dark mode overrides
7. **Verify:** `python -c "from custom.styles import Styles"` must succeed

## CSS to StreamTeX Mapping

| CSS (Marp) | StreamTeX |
|---|---|
| `--color-primary` | `ColorsCustom.primary` |
| `--color-bg` | Background in `themes.py` |
| `--color-text` | Default text color |
| `font-size: Xpx` | Closest `Text.sizes.*` or `Style("font-size: Xpt;")` |
| `font-weight: bold` | `Text.weights.bold_weight` |
| `text-align: center` | `Text.alignments.center_align` |
| `font-style: italic` | `Text.decors.italic_text` |
| `border-left: 4px solid` | `Container.borders.*` |

## Style API — Verified Names

| Category | Correct | WRONG |
|---|---|---|
| `Text.alignments` | `center_align` | `center_txt` |
| `Text.alignments` | `left_align` | `left_txt` |
| `Text.decors` | `italic_text` | `decorations.italic` |
| `Text.decors` | `underline_text` | `underline` |
| `Text` subclass | `decors` | `decorations` |

**Verification:**
```bash
python -c "from streamtex.styles import Text; print(dir(Text.alignments))"
python -c "from streamtex.styles import Text; print(dir(Text.decors))"
```

## Rules

- Dark theme is default — adapt light-theme source colors for dark backgrounds
- Never hardcode black/white — use theme-aware styles
- For custom font sizes not in `Text.sizes.*`, use `Style("font-size: Xpt;", "size_Xpt")`
