Guide the HTML export of a StreamTeX presentation to a self-contained HTML file.

Arguments: $ARGUMENTS (optional: project path, e.g. "projects/project_myproject")

## Steps

1. **Identify the target project**: Use $ARGUMENTS or the current working directory. Read the project's `book.py`.

2. **Check export readiness**:
   - Verify `book.py` imports `ExportConfig` from `streamtex`
   - Verify `ExportConfig(enabled=True)` is passed to `st_book()` via `export_config=`
   - If not configured, add the export configuration:
     ```python
     from streamtex import ExportConfig

     export = ExportConfig(
         enabled=True,
         page_title="My Presentation",
     )
     st_book(module_list, toc_config=toc, export_config=export)
     ```

3. **Audit export-aware widgets**: Scan all `bck_*.py` files for widget usage:
   - `st.dataframe()` -> must be `stx.st_dataframe()`
   - `st.table()` -> must be `stx.st_table()`
   - `st.metric()` -> must be `stx.st_metric()`
   - `st.json()` -> must be `stx.st_json()`
   - `st.line_chart()` -> must be `stx.st_line_chart()`
   - `st.bar_chart()` -> must be `stx.st_bar_chart()`
   - `st.area_chart()` -> must be `stx.st_area_chart()`
   - `st.scatter_chart()` -> must be `stx.st_scatter_chart()`
   - `st.graphviz_chart()` -> must be `stx.st_graphviz()`
   - `st.audio()` -> must be `stx.st_audio()`
   - `st.video()` -> must be `stx.st_video()`
   Report any bare `st.*` widget calls that should be replaced with `stx.*` equivalents.

4. **Check image assets**: Verify all `st_image(uri=...)` references:
   - Local images will be base64-encoded automatically during export
   - URL images will be kept as-is (requires internet access when viewing exported HTML)

5. **Run the export**: Launch the app and instruct the user:
   ```bash
   uv run streamlit run <project>/book.py
   ```
   - The "Download HTML" button will appear in the sidebar when `export_config.enabled=True`
   - Click it to download the self-contained HTML file

6. **Validate the export**: Open the downloaded HTML file in a browser and verify:
   - All text and styles render correctly
   - Images are embedded (base64) or accessible (URLs)
   - Grid layouts and nested containers are preserved
   - Lists render with correct styling

## Advanced: stx.st_export() Context Manager

For fine-grained control over what gets exported, blocks can use:
```python
with stx.st_export(export_config) as exp:
    # Content here is captured for both Streamlit and HTML export
    st_write(s.large, "This appears in both modes")
```

## Troubleshooting

- **Missing content in export**: Ensure all content goes through `stx.*` functions, not raw `st.*`
- **Broken layout**: Check that `st_block`, `st_grid`, `st_list` are properly nested (context managers handle push/pop)
- **Missing images**: Check that image paths are relative to `static/` and `enableStaticServing = true` is in `.streamlit/config.toml`
