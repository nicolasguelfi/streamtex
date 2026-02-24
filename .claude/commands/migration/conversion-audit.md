Audit the quality of a converted StreamTeX block.

## Arguments
- `$ARGUMENTS` — The block name (e.g. `bck_ethics_overview`)

## Workflow

1. **Read the original HTML**:
   - `projects/convert_html_to_streamtex/exports/html/$ARGUMENTS/index.html`

2. **Read the converted StreamTeX block**:
   - `projects/convert_html_to_streamtex/shared/blocks/$ARGUMENTS.py`

3. **Read migration rules**:
   - `.cursor/rules/streamtex/html-migration/RULE.md`
   - `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md`

4. **Run validation**:
   ```bash
   uv run python projects/convert_html_to_streamtex/tools/validate_blocks.py --block $ARGUMENTS
   ```

5. **Audit checklist** — verify each item:
   - [ ] All non-default colors migrated (color-fidelity)
   - [ ] No raw HTML/CSS strings in Python code
   - [ ] Images renamed and referenced via registry
   - [ ] Inline mixed-style text uses ONE st_write() with tuples
   - [ ] Links include font-size when HTML shows text > 12pt
   - [ ] Tables use st_grid() with cell_styles
   - [ ] Lists use st_list() (not hardcoded bullets)
   - [ ] Line breaks use st_br()
   - [ ] No hardcoded black/white (theme-controlled)
   - [ ] Correct family used (pres for bck_*, doc for bckcp_*)
   - [ ] BlockStyles has color-mapping summary
   - [ ] BlockStyles has dropped-colors log

6. **Color sanity check**: Compare 3-5 key colored elements between HTML and StreamTeX.

7. **Report** issues found and suggest fixes.
