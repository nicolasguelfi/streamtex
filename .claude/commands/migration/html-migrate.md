Migrate HTML content to a StreamTeX block.

The user will provide raw HTML (typically from a Google Docs export) either inline or as a file path.

Arguments: $ARGUMENTS (optional: block name or file path to HTML)

## Mandatory Pre-Reading

Before starting, read ALL of these:
1. `.cursor/rules/streamtex/html-migration/RULE.md`
2. `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md`
3. `documentation/streamtex_cheatsheet_en.md`
4. Existing blocks in the target project (for style conventions and patterns already in use)

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
2. **Re-read the migration rules** (both html-migration and color-fidelity).
3. **Fix any mismatches**: update styles, layout, or content.
4. **Run the migration checklist**:
   - [ ] No raw HTML strings
   - [ ] Semantic style names (not c1/c2)
   - [ ] Images renamed per convention
   - [ ] Lists use stx.st_list
   - [ ] Inline content uses ONE st_write with tuples
   - [ ] Font sizes included on link styles where needed
   - [ ] stx.st_br() for line breaks
   - [ ] st_grid with cell_styles for tables
   - [ ] No hardcoded black/white
   - [ ] Bold and italic correctly applied
   - [ ] All non-default text colors mapped
   - [ ] All non-default background/border colors mapped
   - [ ] Color-mapping summary in BlockStyles
   - [ ] Color sanity check passed (3-5 key elements verified)
