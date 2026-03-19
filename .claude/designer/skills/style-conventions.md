# Style Conventions for StreamTeX Slides

## Style Composition

- Use `+` to combine styles: `s.bold + s.large + s.text.colors.blue`
- Use `-` to remove styles: `combined - s.bold`
- Use `Style.create(composed, "style_id")` for themed styles.
- Use `ns("css-property: value;")` only for one-off inline styles.

## Naming

- All custom styles go in `custom/styles.py`.
- Use **English-only** names (no French, no abbreviations).
- Follow the existing naming pattern: `colors.primary_blue`, `containers.good_callout`.

## BlockStyles Class

- Define **only block-local** compositions in `BlockStyles`.
- Always include `heading` and `sub` for consistency.
- Use `bs = BlockStyles` alias for clean code.

## Project Style Hierarchy

```
s.project.colors.*       # Text colors (primary_blue, accent_teal, ...)
s.project.titles.*       # Pre-composed titles (course_title, section_title, ...)
s.project.containers.*   # Container styles (good_callout, bad_callout, code_box, ...)
```

## Theme Support

- NEVER hardcode `color: black` or `background-color: white`.
- Use `style_id` with `Style.create()` for styles that need dark mode overrides.
- Theme overrides go in `custom/themes.py`.

## Helper Functions

| Helper | Purpose | Used for |
|--------|---------|----------|
| `show_code(text)` | Syntax-highlighted code box | All code examples |
| `show_code_inline(text)` | Code without box wrapper | Inside callout containers |
| `show_explanation(text)` | Blue "Purpose" box | Before each example |
| `show_details(text)` | Amber "Details" box | Defaults, tips, after examples |
