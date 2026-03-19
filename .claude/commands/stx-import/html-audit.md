# /stx-import:html-audit — Audit quality of a converted HTML block

Verify the quality of an HTML-to-StreamTeX conversion.

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `<block_name>`

### Examples

```
/stx-import:html-audit bck_ethics_overview
```

## Required readings BEFORE execution

1. `.claude/developer/skills/import-conventions.md` — shared import rules
2. `.claude/import-formats/html/conventions.md` — HTML-specific rules

## Workflow

1. **Read the original HTML** source.

2. **Read the converted StreamTeX block** in `blocks/`.

3. **Read import rules**: Both shared and HTML-specific conventions.

4. **Audit checklist** — verify each item:
   - [ ] All non-default colors migrated (color-fidelity)
   - [ ] No raw HTML/CSS strings in Python code
   - [ ] Images renamed and referenced correctly
   - [ ] Inline mixed-style text uses ONE `st_write()` with tuples
   - [ ] Links include font-size when HTML shows text > 12pt
   - [ ] Tables use `st_grid()` with `cell_styles`
   - [ ] Lists use `st_list()` (not hardcoded bullets)
   - [ ] Line breaks use `st_br()`
   - [ ] No hardcoded black/white (theme-controlled)
   - [ ] Correct family used (pres for `bck_*`, doc for `bckcp_*`)
   - [ ] BlockStyles has color-mapping summary
   - [ ] BlockStyles has dropped-colors log

5. **Color sanity check**: Compare 3-5 key colored elements between HTML and StreamTeX.

6. **Report** issues found and suggest fixes.
