# /stx-import:html — Import HTML content into a StreamTeX block

Migrate HTML content (typically from a Google Docs export) to a StreamTeX block.

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[BLOCK_NAME | FILE_PATH]`

- **BLOCK_NAME**: Name of the block to create (e.g. `bck_ethics_overview`)
- **FILE_PATH**: Path to an HTML file to import

### Examples

```
/stx-import:html bck_ethics_overview
/stx-import:html ./exports/page.html
```

## Required readings BEFORE execution

1. `.claude/developer/agents/import-converter.md` — import agent role
2. `.claude/developer/skills/import-conventions.md` — shared import rules
3. `.claude/import-formats/html/conventions.md` — HTML-specific rules
4. `.claude/references/coding_standards.md` — coding rules
5. Existing blocks in the target project (for style conventions already in use)

## Phase 1: Analysis (Internal)

1. **Filter Noise**: Ignore class names (`c1`, `c12`). Focus on computed styles (bold, centered, blue, etc.).
2. **Identify Defaults**: Black/white text = theme-controlled (do NOT hardcode). Default underlined links = keep default behavior.
3. **Color Audit (MANDATORY)**:
   - Enumerate EVERY `color`, `background-color`, `border-color`, `text-decoration-color` value
   - List all hex/rgb values found
   - For each: map to StreamTeX style OR classify as "default/theme — not migrated" with justification
4. **Detect Formatting**: Bold (`font-weight: 700`) -> `s.bold`, Italic -> `s.italic`
5. **Identify Containers**: Tables -> `stx.st_grid()`, bullet lists -> `stx.st_list()`
6. **Style Consolidation**: Group identical computed styles under ONE generic `BlockStyles` name (English)

## Phase 2: Implementation

1. Create the block file with mandatory imports
2. Define `BlockStyles` class with:
   - Color-mapping summary comment (which HTML colors -> which style names)
   - Dropped-colors log (which colors were intentionally not migrated and why)
   - All consolidated styles
3. Implement `build()`:
   - `stx.st_block()` for stacked sections
   - ONE `st_write()` with tuples for inline mixed-style text (NEVER multiple st_write calls)
   - Include font size in link styles when HTML shows links larger than 12pt
   - `stx.st_grid()` with `cell_styles` for tables
   - `stx.st_list()` for lists
   - `stx.st_br()` for line breaks
4. Rename images: `[block_name]_image_[00index].[ext]` -> copy to `static/images/`

## Phase 3: Second-Pass Verification (MANDATORY)

After the first complete implementation:
1. **Re-read the source HTML** top-to-bottom. For each element, confirm a corresponding structure exists in the block.
2. **Re-read the import rules** (both shared and HTML-specific conventions).
3. **Fix any mismatches**: update styles, layout, or content.
4. **Run the verification checklist** from `.claude/import-formats/html/conventions.md`.
