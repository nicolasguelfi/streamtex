Convert a single HTML block to StreamTeX.

## Arguments
- `$ARGUMENTS` — The block name (e.g. `bck_ethics_overview`)

## Workflow

1. **Read the source HTML**:
   - `projects/convert_html_to_streamtex/exports/html/$ARGUMENTS/index.html`

2. **Read project styles**:
   - `projects/convert_html_to_streamtex/shared/custom/styles.py`

3. **Read migration rules**:
   - `.cursor/rules/streamtex/html-migration/RULE.md`
   - `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md`
   - `documentation/coding_standards.md`

4. **Analyze**: Extract colors, font sizes, layout patterns from the HTML.

5. **Determine family**: If block name starts with `bckcp_` → use `s.project.doc.*` styles. Otherwise → use `s.project.pres.*` styles.

6. **Generate** the StreamTeX block file with:
   - Standard imports (including `from shared.custom.styles import Styles as s`)
   - `BlockStyles` class with color-mapping summary and dropped-colors log
   - `build()` function using StreamTeX components only
   - ONE `st_write()` with tuples for inline mixed-style text
   - `st_grid()` for tables, `st_list()` for lists
   - Font size in link styles to avoid 12pt default
   - Image URIs from the image registry (`tools/image_registry.json`)

7. **Second-pass verification**: Re-read source HTML, check color fidelity, fix mismatches.

8. **Write** the file to `projects/convert_html_to_streamtex/shared/blocks/$ARGUMENTS.py`

9. **Validate**: Run `uv run python projects/convert_html_to_streamtex/tools/validate_blocks.py --block $ARGUMENTS`
