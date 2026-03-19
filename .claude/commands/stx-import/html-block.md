# /stx-import:html-block — Convert a single HTML block to StreamTeX

Convert a specific HTML export into a StreamTeX block file.

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `<block_name>`

### Examples

```
/stx-import:html-block bck_ethics_overview
/stx-import:html-block bckcp_course_intro
```

## Required readings BEFORE execution

1. `.claude/developer/skills/import-conventions.md` — shared import rules
2. `.claude/import-formats/html/conventions.md` — HTML-specific rules
3. `.claude/references/coding_standards.md` — coding rules

## Workflow

1. **Read the source HTML**: Look for exported HTML in the project exports directory.

2. **Read project styles**: Read `custom/styles.py` for available style definitions.

3. **Read import rules**: Both shared conventions and HTML-specific conventions.

4. **Analyze**: Extract colors, font sizes, layout patterns from the HTML.

5. **Determine family**: If block name starts with `bckcp_` → use `s.project.doc.*` styles. Otherwise → use `s.project.pres.*` styles.

6. **Generate** the StreamTeX block file with:
   - Standard imports
   - `BlockStyles` class with color-mapping summary and dropped-colors log
   - `build()` function using StreamTeX components only
   - ONE `st_write()` with tuples for inline mixed-style text
   - `st_grid()` for tables, `st_list()` for lists
   - Font size in link styles to avoid 12pt default

7. **Second-pass verification**: Re-read source HTML, check color fidelity, fix mismatches.

8. **Write** the block file to `blocks/` directory.

9. **Validate**: Run the block to check for import errors.
