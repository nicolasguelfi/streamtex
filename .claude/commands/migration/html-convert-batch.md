Run the batch HTML-to-StreamTeX conversion pipeline.

## Arguments
- `$ARGUMENTS` — Optional flags: `--all`, `--filter "pattern"`, `--dry-run`, `--force`, `--limit N`

## Workflow

1. **Check prerequisites**:
   - Verify `projects/convert_html_to_streamtex/exports/html/` exists
   - Verify `tools/image_registry.json` exists (warn if missing)

2. **Run the batch converter**:
   ```bash
   uv run python projects/convert_html_to_streamtex/tools/batch_convert.py $ARGUMENTS
   ```

3. **Report results**: Show conversion stats (simple/medium/complex/errors).

4. **Validate** generated blocks:
   ```bash
   uv run python projects/convert_html_to_streamtex/tools/validate_blocks.py
   ```

5. **Suggest next steps**: Create blocks.csv files for courses, then run `/project:course-generate --all`.
