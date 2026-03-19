# Step 0 — Detect Target State

> **Runs before analysis.** Audits the current StreamTeX project to detect
> partial migrations, issues, and determine the best migration mode.

## Workflow

1. **Scan `blocks/`** — list all `bck_*.py` files
2. **For each block**, audit for migration quality:
   - Has exactly ONE `toc_lvl="1"` (block root)?
   - All other `toc_lvl` use relative `"+N"` (not absolute `"2"`, `"3"`)?
   - Has `st_slide_break()` between slides? (slides profile)
   - No `st_slide_break()` present? (document profile)
   - Image URIs have no `static/` prefix?
   - Lists use `st_list()` (no `st_write("- ...")`)?
   - No residual markdown in `st_write()` calls (`**`, `- `, `# `, `> `)?
   - BlockStyles references `s.project.slide.*` or `s.project.document.*`?
3. **Scan `book.py`** — detect configuration:
   - Which blocks are wired in `st_book()`?
   - `paginate=True` or `False`? → infer current profile
   - `PresentationConfig` present? → slides profile
   - `ExportMode.MANUAL` or `NEVER`?
   - `sidebar_max_level` value?
4. **Scan `custom/styles.py`** — detect style classes:
   - `SlideStylesCustom` present? → slides profile was used
   - `DocumentStylesCustom` present? → document profile was used
5. **Scan `static/images/`** — list existing images
6. **Compare** with source Marp project (if source path provided)

## Audit Checks per Block

```python
# Pseudo-code for checks performed on each bck_*.py
checks = {
    "toc_root":       count(toc_lvl="1") == 1,
    "toc_relative":   count(toc_lvl="2"|"3"|"4") == 0,
    "slide_breaks":   count(st_slide_break) > 0,       # slides profile
    "no_slide_breaks": count(st_slide_break) == 0,     # document profile
    "uri_no_static":  count(uri="static/) == 0,
    "st_list_used":   count(st_write.*"- ") == 0,
    "no_markdown":    count(**|> |# ) in st_write == 0,
}
```

## Output: Migration Status Report

```markdown
## Target Project State

**Detected profile:** slides (PresentationConfig present, paginate=True)
**Blocks found:** 12
**Blocks in book.py:** 12

### Block Audit

| Block | toc_root | toc_relative | slide_breaks | URIs | lists | markdown |
|---|---|---|---|---|---|---|
| bck_title | ok | ok | N/A | ok | ok | ok |
| bck_day1_tools | ok | ok | ok (34) | ok | ok | ok |
| bck_day1_install | ok | FAIL (abs) | ok | ok | ok | ok |

### Issues Summary

- 9 blocks use absolute toc_lvl ("2", "3") instead of relative ("+1", "+2")
- 0 blocks have static/ prefix in image URIs
- 0 blocks have residual markdown

### Source-Target Comparison

| Source File | Target Block | Status |
|---|---|---|
| slides/day1/01_tools.md | bck_day1_tools.py | MIGRATED |
| slides/day1/02_install.md | bck_day1_install.py | MIGRATED (issues) |
| slots/day1/01_tools.md | — | NOT MIGRATED |
```

## Migration Mode Recommendation

Based on the audit, recommend one of:

### FULL mode (`--mode full`)
- **When:** No existing blocks, or user wants to start over
- **Action:** Delete all `bck_*.py` (except non-Marp blocks), regenerate everything
- **Warning:** Destructive — ask for explicit confirmation

### INCREMENTAL mode (`--mode incremental`)
- **When:** Some blocks already migrated correctly, others missing
- **Action:** Convert only missing source files, skip existing blocks
- **Warning:** Existing blocks keep their current issues (if any)

### FIX mode (`--mode fix`)
- **When:** All blocks exist but have quality issues
- **Action:** Keep block content, fix detected issues:
  - Convert absolute `toc_lvl` to relative `"+N"`
  - Fix image URIs (remove `static/` prefix)
  - Add missing `st_slide_break()` (slides profile)
  - Replace `st_write("- ...")` with `st_list()`
- **Warning:** Modifies existing files in-place

## Interaction

After generating the report, ask the user:

```
Migration state detected. Choose an action:
1. FULL      — Re-import everything from scratch (deletes existing blocks)
2. INCREMENTAL — Convert only missing files, keep existing blocks as-is
3. FIX       — Keep all blocks, fix detected issues in-place
4. ABORT     — Do nothing, review the report first

Which mode? [1/2/3/4]:
```

Proceed to step 1 (analyze) only after user confirms.
