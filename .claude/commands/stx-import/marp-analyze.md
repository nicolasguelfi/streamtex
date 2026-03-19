# /stx-import:marp-analyze — Analyze a Marp project before import

Inventory a Marp presentation project, audit the current target state, and produce a migration report without modifying any files.

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `<source_directory>`

### Examples

```
/stx-import:marp-analyze ../marp-slides
/stx-import:marp-analyze ../marp-course
```

## Required readings BEFORE execution

1. `.claude/developer/agents/import-converter.md` — import agent role
2. `.claude/developer/skills/import-conventions.md` — shared import rules
3. `.claude/import-formats/marp/conventions.md` — Marp-specific rules

## What it does

### Part 1 — Target state detection (step 00)

Read and execute `.claude/import-formats/marp/steps/00-detect-target.md`:

1. **Scan** existing `blocks/`, `book.py`, `custom/styles.py`, `static/images/`
2. **Audit** each existing block for migration quality:
   - toc_lvl relative (`"+N"`) or absolute (`"2"`, `"3"`)?
   - slide breaks present?
   - image URIs without `static/` prefix?
   - lists using `st_list()` (no simulated markdown)?
3. **Detect** current profile (slides vs document) from `book.py` config
4. **Generate** block audit table with per-block issue count

### Part 2 — Source analysis (step 01)

Read and execute `.claude/import-formats/marp/steps/01-analyze.md`:

1. **Scan** the source directory for Marp files (`.md` with `marp: true` frontmatter)
2. **Extract** metadata: title, slide count, instructor, duration
3. **Inventory** images: referenced, existing, missing
4. **Detect** theme CSS, colors, fonts
5. **Detect** slots (instructor notes) if present

### Part 3 — Comparison and recommendation

1. **Compare** source files ↔ existing target blocks
2. **Classify** each source file as: MIGRATED, MIGRATED (issues), PARTIAL, NOT MIGRATED
3. **Recommend** migration mode:
   - `full` — if no blocks exist or many issues
   - `incremental` — if most blocks OK, some missing
   - `fix` — if all blocks exist but have quality issues

## Output

A Markdown report printed to the user (not saved to file) with:

1. **Target state** — existing blocks, detected profile, audit results
2. **Source summary** — files, slides, images, theme
3. **Comparison table** — source ↔ target mapping with status
4. **Issues summary** — counts of each issue type across all blocks
5. **Recommended action** — suggested `--mode` and `--profile` for `/stx-import:marp`

## Rules

- **Read-only** — do not create, modify, or delete any files
- Report all findings to the user for review before running `/stx-import:marp`
