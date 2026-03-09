# StreamTeX Library Architecture

Reference for library contributors working on `streamtex/` source code.

## Module Dependency Graph

```
__init__.py (public API re-exports)
  |
  +-- styles/ (independent, no deps on other streamtex modules)
  |     base.py -> core.py -> text.py, container.py, visibility.py
  |     __init__.py re-exports: Style, ListStyle, StyleGrid, StxStyles, theme
  |
  +-- enums.py (Tags, ListTypes — independent)
  +-- constants.py (PAGE_WIDTH, PAGE_PADDING — configurable defaults)
  +-- utils.py (generate_key, contain_link, inject_link_preview_scaffold — independent)
  |
  +-- write.py (st_write) -> styles, enums, export
  +-- container.py (st_block, st_span) -> styles, export
  +-- grid.py (st_grid) -> styles, export
  +-- list.py (st_list) -> styles, enums, export
  +-- image.py (st_image) -> styles, image_utils, export
  +-- image_utils.py (MIME detection, URL validation — independent)
  +-- code.py (st_code) -> styles, export
  +-- space.py (st_space, st_br) -> export
  +-- overlay.py (st_overlay) -> styles, export
  |
  +-- export.py (ExportConfig, HtmlExportBuffer, st_export) -> constants
  +-- export_widgets.py (st_dataframe, st_table, ...) -> export
  |
  +-- toc.py (TOCConfig, reset_toc_registry, toc_entries) -> independent singleton
  +-- marker.py (MarkerConfig, st_marker) -> toc
  +-- book.py (st_book, st_include, st_toc, load_css) -> toc, marker, export, zoom
  +-- zoom.py (add_zoom_options, inject_zoom_logic) -> constants
  +-- slide.py (SlideBreakMode, SlideBreakConfig, st_slide_break, add_slide_break_options, inject_slide_break_css) -> constants
  |
  +-- ai/ (AI image generation)
  |     config.py (AIImageConfig, set/get_ai_image_config — DI singleton)
  |     generate.py (generate_image, is_cached, _make_cache_key — file-based cache)
  |     providers/ (registry + OpenAI, Google Imagen 4, fal.ai adapters)
  +-- ai_image.py (st_ai_image, st_ai_image_widget) -> ai/, image
  |
  +-- blocks.py (LazyBlockRegistry, ProjectBlockRegistry, static resolution) -> independent
  +-- block_helpers.py (BlockHelper, show_code/explanation/details, DI config) -> code, container, write, styles
  |
  +-- collection.py (st_collection, CollectionConfig, ProjectMeta) -> styles, book
  +-- link_preview.py (inject_link_preview_scaffold) -> independent
  +-- search.py (TextCollector, search engine — WIP, NOT exported)
```

## Key Design Patterns

### 1. Dual Rendering Pipeline (export.py)

Every content function (`st_write`, `st_block`, `st_grid`, etc.) calls `_render()` which:
1. Sends HTML to Streamlit via `st.html()` (live display)
2. Appends the same HTML to `HtmlExportBuffer` if export is active

The buffer uses a **push/pop stack** for nesting:
- `st_block` → `push_wrapper("<div ...>")` on enter, `pop_wrapper("</div>")` on exit
- `st_grid` → push grid wrapper, cells are appended, pop on exit
- `st_list` → push `<ul>`/`<ol>`, items push/pop `<li>`, pop list on exit

### 2. Global Singleton Registries

Both `toc.py` and `marker.py` use module-level singleton registries:
- `toc.py`: `_toc_entries: list` — accumulated by `st_write(toc_lvl=...)` calls
- `marker.py`: `_markers: list` — accumulated by `st_marker()` calls
- Both reset per `st_book()` run to avoid duplication on Streamlit reruns

### 3. Dependency Injection for Block Helpers

`block_helpers.py` uses a config object pattern:
- `BlockHelperConfig` defines abstract methods: `get_code_style()`, `get_explanation_style()`, etc.
- `set_block_helper_config(config)` sets the global config once at startup (in `blocks/helpers.py`)
- `show_code()`, `show_explanation()`, `show_details()` read the config to get their container styles
- Projects can swap configs at runtime or override via OOP inheritance

### 4. Lazy Block Loading

`ProjectBlockRegistry` and `LazyBlockRegistry` use `importlib.util.spec_from_file_location()` to load block modules on demand. `blocks/__init__.py` uses `__getattr__` to intercept attribute access and trigger lazy loading.

### 5. Static Asset Resolution

`set_static_sources([path1, path2, ...])` registers search paths. `resolve_static(filename)` returns the first match. Used by `st_image` to find assets across project + shared block directories.

### 6. CSS Zoom (not transform)

`zoom.py` uses the CSS `zoom` property (Baseline 2024, supported by all modern browsers) rather than `transform: scale()`. Pure CSS — no JavaScript, no ResizeObserver. Two independent sidebar controls: Width % (page width as % of browser) and Zoom % (CSS zoom on content).

## Module Categories

| Category | Modules | Responsibility |
|----------|---------|---------------|
| **Styles** | `styles/` | CSS generation, composition, theming |
| **Rendering** | `write`, `container`, `grid`, `list`, `image`, `code`, `space`, `overlay` | Content → HTML |
| **Navigation** | `toc`, `marker`, `zoom` | TOC, keyboard nav, zoom |
| **Orchestration** | `book`, `collection` | Page flow, multi-project |
| **Export** | `export`, `export_widgets` | HTML export pipeline |
| **AI** | `ai/`, `ai_image` | AI image generation (OpenAI, Google, fal.ai) |
| **Infrastructure** | `blocks`, `block_helpers`, `utils`, `constants`, `enums` | DI, registries, enums |
| **WIP** | `search` | Full-text search (not exported) |

### 7. AI Image Generation (ai/, ai_image.py)

3-layer architecture following the same DI pattern as GSheetConfig/LinkConfig:
- **Presentation** (`ai_image.py`): `st_ai_image()`, `st_ai_image_widget()` — delegates to `st_image` for display
- **Service** (`ai/generate.py`): `generate_image()`, `is_cached()` — file-based deterministic cache (hash of prompt+provider+size+quality+seed)
- **Providers** (`ai/providers/`): Abstract base `AIImageProvider` + registry + 3 adapters (OpenAI, Google Imagen 4, fal.ai)

Optional dependencies: `streamtex[ai]`, `streamtex[ai-openai]`, `streamtex[ai-google]`, `streamtex[ai-fal]`.
Provider SDKs are imported lazily inside `generate()` — missing SDK raises a clear `ImportError` with install instructions.

## Testing Strategy

- Each module has a corresponding `tests/test_<module>.py`
- Tests mock `st.html()` and inspect the HTML output
- `test_export_guard.py` uses AST scanning to ensure no unauthorized `st.html()` calls
- Integration tests in `tests/test_book_integration.py`
- Shared fixtures in `tests/conftest.py`

## Adding a New Module

1. Create `streamtex/new_module.py`
2. If it renders content, integrate with `export.py` (call `_render()` or buffer API)
3. Export public symbols from `streamtex/__init__.py`
4. Create `tests/test_new_module.py`
5. Run `uv run pytest tests/ -v`
6. Update `documentation/coding_standards.md` and cheatsheets
