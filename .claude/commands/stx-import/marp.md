# /stx-import:marp — Import a Marp project into StreamTeX

Convert an entire Marp presentation project into a StreamTeX project in the current working directory.

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `<source_directory> [OPTIONS]`

**Options**:
- `--profile slides` (default) — Projection-optimized: large fonts, telegraphic, paginated, dark
- `--profile document` — Reading-optimized: full text, continuous scroll, helper boxes, dark/light
- `--mode full` (default) — Re-import everything from scratch
- `--mode incremental` — Convert only missing files, keep existing blocks as-is
- `--mode fix` — Keep all blocks, fix detected issues in-place (URIs, toc_lvl, slide breaks)
- `--no-slots` — Skip instructor notes conversion (step 5)
- `--dry-run` — Show what would be created without writing files
- `--help` — Show profile comparison and workflow overview

### Examples

```
/stx-import:marp ../marp-slides --profile slides
/stx-import:marp ../marp-course --profile document --mode incremental
/stx-import:marp ../slides --mode fix
/stx-import:marp --help
```

### Profile comparison

| Aspect | `slides` | `document` |
|---|---|---|
| Fonts | 48pt+ body, 64pt headline | 24pt body, 48pt headline |
| Content | Condensed, telegraphic | Full sentences preserved |
| Layout | Paginated, slide breaks | Continuous scroll |
| Slots | Skipped by default | Integrated via helper boxes |
| PresentationConfig | Active (16:9 footer) | Omitted |
| Helper boxes | Never | `show_explanation()`, `show_details()` |

## Required readings BEFORE execution

1. `.claude/developer/agents/import-converter.md` — import agent role
2. `.claude/developer/skills/import-conventions.md` — shared import rules
3. `.claude/import-formats/marp/conventions.md` — Marp-specific rules
4. `.claude/import-formats/marp/profiles/{profile}.md` — active profile
5. `.claude/references/coding_standards.md` — coding rules

## What it does

Converts Marp Markdown slides, CSS themes, images, and optionally instructor notes
into native StreamTeX blocks with full graphical quality and responsive design.

**Principle: Zero residual Markdown** — every Marp element is converted to a native `stx.*` component.

## Workflow

Execute each step in order. Each step is documented in `.claude/import-formats/marp/steps/`.
**Every step MUST read the active profile first** to determine sizes, content rules, and layout.

### Step 0 — Detect target state (`steps/00-detect-target.md`)
- Audit existing `blocks/`, `book.py`, `custom/styles.py`, `static/images/`
- For each existing block, check: toc_lvl relative, slide breaks, image URIs, no markdown
- Compare source ↔ target to find migrated, partially migrated, and missing blocks
- **Generate migration status report**
- If `--mode` not specified, **recommend a mode** (full/incremental/fix) based on findings
- **Ask user for confirmation** of mode before proceeding

### Step 1 — Analyze (`steps/01-analyze.md`)
- Inventory source files, count slides, list images
- Detect theme CSS, extract colors
- Map source files to target block names
- Report which profile will be used
- **Ask user for confirmation** before proceeding

### Step 2 — Migrate theme (`steps/02-theme-migrate.md`)
- Read the active profile for font sizes and style names
- **slides:** Generate `SlideStylesCustom` (64pt headline, 48pt body)
- **document:** Generate `DocumentStylesCustom` (48pt headline, 24pt body)
- Convert Marp CSS theme colors to `custom/styles.py` and `custom/themes.py`
- **CRITICAL:** Use correct API names (`Text.alignments.center_align`, `Text.decors.italic_text`)
- Verify with: `python -c "from custom.styles import Styles"`

### Step 3 — Migrate assets (`steps/03-assets-migrate.md`)
- Copy images to `static/images/day{N}/`
- For missing images, generate placeholder code with IMAGE PROMPT comments
- **CRITICAL:** Image URIs are relative to static source — `images/day1/file.png`, NOT `static/images/...`

### Step 4 — Convert blocks (`steps/04-convert-block.md`)
- Read the active profile for content rules
- Convert each slide file to one or more StreamTeX blocks
- Apply Zero Residual Markdown rules (all content via `stx.*` components)
- **Profile-specific behavior:**
  - **slides:** Condense text, telegraphic bullets, `st_slide_break()` between slides
  - **document:** Preserve full text, no `st_slide_break()`, use `st_br()` for separation
- **CRITICAL TOC hierarchy** (same for both profiles):
  - `toc_lvl="1"` — ONE per block (absolute root)
  - `toc_lvl="+1"` — Sections and standalone slides
  - `toc_lvl="+2"` — Slides under a section
  - NEVER use absolute `"2"`, `"3"` — always relative `"+N"`

### Step 5 — Convert slots (`steps/05-slot-convert.md`)
- Read the active profile for slot handling rules
- **slides:** Skip by default. If included, extract only key bullets.
- **document:** Fully integrate via `show_explanation()` and `show_details()`
- Skip entirely with `--no-slots`

### Step 6 — Configure book.py (`steps/06-configure-book.md`)
- Read the active profile for book.py configuration
- Wire all blocks in `st_book()` in chronological order
- **slides:** `paginate=True`, `PresentationConfig(...)`, `page_width=100`, `zoom=80`
- **document:** `paginate=False`, no `PresentationConfig`, `page_width=90`, `zoom=100`
- **Common defaults:**
  - `ExportMode.MANUAL` (not `NEVER`) for HTML and PDF exports
  - `sidebar_max_level=3` in TOCConfig
  - `auto_marker_on_toc=1` in MarkerConfig
- Verify: `python -c "import setup; import blocks"` (all blocks load)

## Post-import checklist

After all steps complete, verify:

- [ ] Active profile applied correctly (check font sizes, pagination mode)
- [ ] All images copied to `static/images/` and URIs have no `static/` prefix
- [ ] All blocks have exactly ONE `toc_lvl="1"` and all others use `"+N"`
- [ ] **slides:** Every slide has a `st_slide_break()` before it
- [ ] **document:** No `st_slide_break()`, only `st_br()` separators
- [ ] No markdown syntax in any `st_write()` calls
- [ ] All enumerations use `st_list()`, not `st_write("- ...")`
- [ ] Exports are `ExportMode.MANUAL`
- [ ] Style API uses correct names (`center_align`, `italic_text`, `decors`)
- [ ] `stx run` launches without errors
