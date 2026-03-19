# /stx-import:html-batch — Batch convert HTML files to StreamTeX blocks

Run a batch HTML-to-StreamTeX conversion pipeline.

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `--all` — Convert all HTML exports found
- `--filter "pattern"` — Only convert blocks matching pattern
- `--dry-run` — Show what would be converted without executing
- `--force` — Overwrite existing blocks
- `--limit N` — Convert at most N blocks

### Examples

```
/stx-import:html-batch --all
/stx-import:html-batch --filter "bck_ethics_*" --dry-run
/stx-import:html-batch --all --force --limit 5
```

## Required readings BEFORE execution

1. `.claude/developer/skills/import-conventions.md` — shared import rules
2. `.claude/import-formats/html/conventions.md` — HTML-specific rules

## Workflow

1. **Check prerequisites**: Verify HTML exports directory exists.

2. **Discover blocks**: Scan for exportable HTML files, apply filter if specified.

3. **Display plan**: Show list of blocks to convert with estimated complexity.

4. **Convert each block**: Execute `/stx-import:html-block` for each discovered block.

5. **Report results**: Show conversion stats (success/warning/error counts).

6. **Validate**: Run validation on all generated blocks.

7. **Suggest next steps**: Create blocks.csv files for courses if applicable.
