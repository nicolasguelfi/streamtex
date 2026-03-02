# Responsive Sizing System

**Version**: 0.2.0
**Date**: 2026-02-25
**Status**: Implemented
**Tests**: 785/785 passed, ruff clean

## Context

The CSS `zoom` property used by `zoom.py` for desktop resizing does not work reliably on mobile browsers:
- **iOS Safari**: `zoom` is not supported
- **Android Chrome**: partial/inconsistent behavior

Rather than patching zoom for mobile, StreamTeX introduces a **responsive sizing system** based on CSS custom properties (`var()`) and viewport `@media` breakpoints. Content automatically adapts on tablets and phones without breaking desktop rendering or modifying the library architecture.

## Files Modified

### Library source (4 files)

| File | Change |
|---|---|
| `streamtex/static/default.css` | Added 44 CSS custom properties in `:root` + tablet `@media (max-width: 1024px)` + mobile `@media (max-width: 480px)` breakpoints |
| `streamtex/styles/text.py` | `Sizes` class: 13 pt-scale constants → `var(--stx-*-size, Npt)` |
| `streamtex/styles/container.py` | `Paddings` (12), `Margins` (12), `GridStyles` (6) → `var()` with fallbacks |
| `streamtex/constants.py` | `PAGE_PADDING` changed from `"36pt"` to `"var(--stx-page-padding, 36pt)"` |

### Tests (3 files)

| File | Change |
|---|---|
| `tests/test_styles.py` | Lines 208-209: assertions updated to match `var()` syntax (`"--stx-medium-size, 16pt"` instead of `"font-size: 16pt;"`) |
| `tests/test_zoom.py` | Lines 48-49: padding assertions updated to match `var(--stx-page-padding, 36pt)` |
| `tests/test_export.py` | Line 33: `ExportConfig` default `page_padding` assertion updated |

### Documentation (1 file)

| File | Change |
|---|---|
| `documentation/maintenance/maintenance_responsive_sizing.md` | This file (created) |

## Architecture

### CSS Custom Properties + @media Breakpoints

The system uses three layers:

1. **`:root` variables** in `default.css` define desktop defaults
2. **`@media (max-width: 1024px)`** overrides for tablet
3. **`@media (max-width: 480px)`** overrides for mobile

### Zero-breakage Principle

Every Python style uses `var(--stx-xxx, fallback)` where the fallback is the original desktop value:

```python
# Before
Giant_size = Style("font-size: 128pt;", "Giant_size")

# After
Giant_size = Style("font-size: var(--stx-Giant-size, 128pt);", "Giant_size")
```

If the CSS variable is not defined (e.g., old `default.css` cached), the fallback ensures identical desktop rendering.

### How var() flows through the system

- `Style` class (`core.py`) stores CSS as raw string — `var()` passes through untouched
- `st_write` (`write.py`) injects CSS into `style=""` attributes — `var()` works in inline styles
- `st_block` (`container.py`) injects CSS into `<style>` blocks — `var()` works there too
- HTML export bundles `default.css` — responsive variables work in exported HTML
- Desktop zoom (`zoom.py`) composes independently after variable resolution

## Value Tables

### Font Sizes

| Variable | Desktop | Tablet (<=1024px) | Mobile (<=480px) |
|---|---|---|---|
| `--stx-GIANT-size` | 196pt | 128pt (65%) | 80pt (41%) |
| `--stx-Giant-size` | 128pt | 84pt (66%) | 56pt (44%) |
| `--stx-giant-size` | 112pt | 74pt (66%) | 48pt (43%) |
| `--stx-Huge-size` | 96pt | 64pt (67%) | 42pt (44%) |
| `--stx-huge-size` | 80pt | 54pt (68%) | 36pt (45%) |
| `--stx-LARGE-size` | 64pt | 48pt (75%) | 32pt (50%) |
| `--stx-Large-size` | 48pt | 36pt (75%) | 26pt (54%) |
| `--stx-large-size` | 32pt | 26pt (81%) | 20pt (63%) |
| `--stx-big-size` | 24pt | 20pt (83%) | 17pt (71%) |
| `--stx-medium-size` | 16pt | 15pt (94%) | 14pt (88%) |
| `--stx-little-size` | 12pt | 12pt (100%) | 11pt (92%) |
| `--stx-small-size` | 8pt | 8pt (100%) | 7pt (88%) |
| `--stx-tiny-size` | 4pt | 4pt (100%) | 4pt (100%) |

### Paddings

| Variable | Desktop | Tablet | Mobile |
|---|---|---|---|
| `--stx-Giant-padding` | 96pt | 64pt | 42pt |
| `--stx-giant-padding` | 84pt | 56pt | 36pt |
| `--stx-Huge-padding` | 72pt | 48pt | 32pt |
| `--stx-huge-padding` | 60pt | 40pt | 26pt |
| `--stx-LARGE-padding` | 48pt | 32pt | 22pt |
| `--stx-Large-padding` | 36pt | 24pt | 16pt |
| `--stx-large-padding` | 24pt | 18pt | 12pt |
| `--stx-big-padding` | 18pt | 14pt | 10pt |
| `--stx-medium-padding` | 12pt | 10pt | 8pt |
| `--stx-little-padding` | 9pt | 8pt | 7pt |
| `--stx-small-padding` | 6pt | 6pt | 5pt |
| `--stx-tiny-padding` | 3pt | 3pt | 3pt |

### Margins

| Variable | Desktop | Tablet | Mobile |
|---|---|---|---|
| `--stx-Giant-margin` | 96pt | 64pt | 42pt |
| `--stx-giant-margin` | 84pt | 56pt | 36pt |
| `--stx-Huge-margin` | 72pt | 48pt | 32pt |
| `--stx-huge-margin` | 60pt | 40pt | 26pt |
| `--stx-LARGE-margin` | 48pt | 32pt | 22pt |
| `--stx-Large-margin` | 36pt | 24pt | 16pt |
| `--stx-large-margin` | 24pt | 18pt | 12pt |
| `--stx-big-margin` | 18pt | 14pt | 10pt |
| `--stx-medium-margin` | 12pt | 10pt | 8pt |
| `--stx-little-margin` | 9pt | 8pt | 7pt |
| `--stx-small-margin` | 6pt | 6pt | 5pt |
| `--stx-tiny-margin` | 3pt | 3pt | 3pt |

### Grid Gaps

| Variable | Desktop | Tablet | Mobile |
|---|---|---|---|
| `--stx-gap-48` | 48px | 32px | 24px |
| `--stx-gap-32` | 32px | 24px | 16px |
| `--stx-gap-24` | 24px | 16px | 12px |
| `--stx-gap-16` | 16px | 12px | 8px |
| `--stx-gap-12` | 12px | 10px | 8px |
| `--stx-gap-8` | 8px | 6px | 4px |

### Page Padding

| Variable | Desktop | Tablet | Mobile |
|---|---|---|---|
| `--stx-page-padding` | 36pt | 24pt | 12pt |

## Consequences on Library Features

### Inherited responsive behavior (no code change needed)

| Component | Why |
|---|---|
| `Titles.title` | Composes from `Sizes.LARGE_size` → now responsive |
| `Titles.subtitle` | Composes from `Sizes.large_size` → now responsive |
| `StxStyles.GIANT`, `.Giant`, ..., `.tiny` | Aliases to `Sizes.*_size` → all responsive |
| `StxStyles.container.paddings.*` | Aliases to `Paddings.*` → all responsive |
| `StxStyles.container.margins.*` | Aliases to `Margins.*` → all responsive |
| `StxStyles.container.grid.*` | Aliases to `GridStyles.*` → all responsive |
| Any user `Style` composed with `+` from these | Inherits `var()` CSS strings |

### Indirect impacts (behavior preserved, CSS output changed)

| Component | Impact |
|---|---|
| `zoom.py` (`inject_zoom_logic`) | Imports `PAGE_PADDING` from `constants.py` → generated CSS now contains `var(--stx-page-padding, 36pt)` instead of `36pt`. Behavior identical on desktop (variable resolves to same value), responsive on mobile. |
| `ExportConfig` (`export.py`) | Default `page_padding` is now `var(--stx-page-padding, 36pt)`. Exported HTML benefits from responsive variables since `default.css` is bundled. |
| `grid.py` export mode | Grid gaps flow into export HTML via inline `gap:` values — responsive `var()` values work in exported HTML too. |

### Browser compatibility

`var()` in inline `style=""` attributes is supported in all modern browsers (Chrome 49+, Firefox 31+, Safari 9.1+, Edge 15+). **Not supported in IE11.** This is not a concern since Streamlit itself requires modern browsers.

## What is NOT affected

| Element | Reason |
|---|---|
| `Style` class (`styles/core.py`) | No modification to the CSS engine |
| `em`/`px` scales in `text.py`, `container.py` | Already relative or intentionally fixed |
| `none_padding`, `none_margin`, `auto_margin`, `gap_0` | Zero/auto invariant to viewport |
| `zoom.py` source code | No code change — only its CSS output changes via `PAGE_PADDING` import |
| Factory methods `Sizes.size()`, `Paddings.size()`, `Margins.size()` | Produce custom fixed sizes by design |
| `Borders.size()` factory | Border widths are intentionally fixed |
| HTML export | Benefits automatically (default.css bundled) |
| Existing projects | Desktop rendering strictly identical (fallbacks = current values) |
| `remove_css()` | Works because `var(...)` contains no unquoted `;` |

## Project Customization

Projects can override responsive breakpoints by adding a `<style>` block in their `book.py`:

```python
import streamlit as st

st.html("""
<style>
@media (max-width: 480px) {
    :root {
        --stx-Giant-size: 40pt;   /* Even smaller on mobile */
        --stx-page-padding: 8pt;  /* Tighter margins */
    }
}
</style>
""")
```

This overrides the library defaults for that specific project.

## Relationship with Zoom

The zoom system (`zoom.py`) and responsive sizing are **complementary**:

- **Responsive sizing** adapts *individual property values* based on viewport width
- **Zoom** scales the *entire page content* uniformly via CSS `zoom`

On desktop, zoom works as before. On mobile where `zoom` is unsupported, responsive sizing ensures the content is still readable. When both are active, responsive variables resolve first, then zoom scales the result.

## Verification

### Automated (2026-02-25)

| Check | Result |
|---|---|
| `uv run pytest tests/ -v` | **785/785 passed** (3.64s) |
| `uv run ruff check streamtex/` | **All checks passed** |

### Manual (to perform)

```bash
# Visual test desktop (must be identical to pre-change)
uv run streamlit run documentation/manuals/stx_manual_intro/book.py

# Visual test mobile (DevTools -> responsive 480px)
# -> titles should shrink, body text stays readable

# HTML export test
# -> export then open on mobile -> responsive too
```
