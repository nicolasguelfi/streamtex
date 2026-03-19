Create a new slide (block file) for a StreamTeX presentation project.

Arguments: $ARGUMENTS (slide name and description, e.g. "bck_zoom - Zoom controls demo")

## Steps

1. **Load rules**: Read `.claude/designer/skills/visual-design-rules.md` for the full design ruleset.
2. **Read style conventions**: Read `.claude/designer/skills/style-conventions.md`.
3. **Parse arguments**: Extract block name (must follow `bck_description` format — semantic name, no numbered prefix).
4. **Determine target project**: Use current working directory or ask the user.
5. **Create the block file** in `[project]/blocks/` with:
   - Standard imports including `from blocks.helpers import show_code, show_explanation, show_details`
   - `BlockStyles` class with `heading` and `sub` styles
   - `bs = BlockStyles` alias
   - `build()` function wrapping all content in `with st_block(s.center_txt):`
   - Main heading with `tag=t.div, toc_lvl="1"`
   - Each subsection following the canonical structure:
     - `st_write(bs.sub, ..., toc_lvl="+1")` + `st_space("v", 1)`
     - `show_explanation("""\...""")`  + `st_space("v", 1)`
     - `show_code("""\...""")` + `st_space("v", 1)`
     - Live rendering + `st_space("v", 2)`
     - Optional `show_details("""\...""")` with defaults
6. **Validate**:
   - No line of visible text exceeds ~45 characters
   - Every live rendering has a preceding `show_code()`
   - All multi-line text blocks use `"""\..."""`
   - Body text uses `s.large` (32pt)
   - No concatenated multi-string `st_write()` calls
7. **Show wiring**: Tell user how to add to `book.py` module list.

## Constraints
- Follow ALL rules from `.claude/designer/skills/visual-design-rules.md`
- No raw HTML/CSS strings
- Use `st_write()` + `st_br()` for multi-line text, not string concatenation
- Use `s.large` for all body text
