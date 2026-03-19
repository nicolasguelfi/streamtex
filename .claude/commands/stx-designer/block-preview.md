Preview and validate a StreamTeX block by checking its structure and dependencies.

Arguments: $ARGUMENTS (block file path, e.g. "documentation/manuals/stx_manual_intro/blocks/bck_level_badge.py")

## Steps

1. **Read the block file** at the specified path.

2. **Structural validation** — check and report:
   - [ ] Has mandatory imports (streamtex, styles, enums, custom.styles)
   - [ ] Has `BlockStyles` class (or `BStyles`) with `bs` alias
   - [ ] Has `build()` function
   - [ ] No raw HTML strings (`<div`, `<span`, `<style`, `unsafe_allow_html`)
   - [ ] No raw CSS strings (inline `"color:"`, `"font-size:"`, etc. outside of `Style()` or `ns()`)
   - [ ] Uses `stx.*` functions, not raw `st.*` for content

3. **Asset validation**:
   - Extract all `uri=` values from `st_image()` calls
   - Check each image exists in the project's `static/images/` directory
   - Check image naming follows convention: `[block_name]_image_[00index].[ext]`
   - Report any missing or misnamed images

4. **Style validation**:
   - List all styles referenced in the block
   - Check each resolves to a defined style (in `BlockStyles`, `custom/styles.py`, or `streamtex.styles`)
   - Flag any undefined style references

5. **TOC analysis**:
   - List all `toc_lvl=` entries found in the block
   - Show the heading hierarchy that would be generated
   - Flag any level jumps > 1 (e.g., going from level 1 to level 3)

6. **Layout analysis**:
   - Count grids, blocks, spans, lists, overlays used
   - Check nesting depth (warn if > 4 levels deep)
   - Check for multiple `st_write` calls that should use tuples

7. **Report**: Provide a structured summary:
   ```
   Block: [filename]
   Status: [PASS / WARNINGS / ERRORS]
   Structure: [OK / issues]
   Assets: [N images, M missing]
   Styles: [N defined, M referenced, P unresolved]
   TOC: [heading hierarchy]
   Layout: [grid/block/list/overlay counts]
   Issues: [list of problems with line numbers]
   ```
