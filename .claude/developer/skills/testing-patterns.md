# StreamTeX Testing Patterns

Reference for library contributors writing and maintaining tests.

## Running Tests

```bash
uv run pytest tests/ -v                      # All tests
uv run pytest tests/test_write.py -v         # Single module
uv run pytest tests/test_write.py -k "test_tuple" -v  # Single test
uv run pytest tests/ -v --tb=short           # Short tracebacks
```

## Test File Inventory (19 files)

| File | Module Tested | Key Focus |
|------|---------------|-----------|
| `test_styles.py` | `styles/` | Style composition (+/-), CSS generation, `Style.create()` |
| `test_enums.py` | `enums.py` | Tags, ListTypes enum values |
| `test_write.py` | `write.py` | `st_write()`, tuple syntax, links, TOC registration |
| `test_container.py` | `container.py` | `st_block()`, `st_span()` nesting |
| `test_grid.py` | `grid.py` | `st_grid()`, `StyleGrid`, cell styling |
| `test_list.py` | `list.py` | `st_list()`, ordered/unordered, nesting |
| `test_image.py` | `image.py` | `st_image()`, base64, clickable, hover |
| `test_code.py` | `code.py` | `st_code()`, syntax highlighting, line numbers |
| `test_space.py` | `space.py` | `st_space()`, `st_br()` |
| `test_overlay.py` | `overlay.py` | `st_overlay()`, layer positioning |
| `test_toc.py` | `toc.py` | TOC registry, auto-numbering, `TOCConfig` |
| `test_marker.py` | `marker.py` | `MarkerConfig`, marker registration |
| `test_export.py` | `export.py` | `HtmlExportBuffer`, push/pop stack, full export |
| `test_export_guard.py` | All modules | AST scan: no unauthorized `st.html()` calls |
| `test_export_widgets.py` | `export_widgets.py` | Widget wrappers, export buffer integration |
| `test_lazy_blocks.py` | `blocks.py` | `LazyBlockRegistry`, `ProjectBlockRegistry` |
| `test_collection.py` | `collection.py` | `CollectionConfig`, `ProjectMeta`, TOML loading |
| `test_book_integration.py` | `book.py` | `st_book()` end-to-end, pagination, TOC integration |
| `test_utils.py` | `utils.py` | `generate_key()`, `contain_link()` |

## Shared Fixtures (`conftest.py`)

The `conftest.py` file provides pytest fixtures shared across all test files. Check it before writing new tests to avoid duplication.

## Common Test Patterns

### 1. Mocking `st.html()` to Capture Output

Most rendering functions ultimately call `st.html()`. Tests mock it to inspect the generated HTML:

```python
from unittest.mock import patch, MagicMock

def test_st_write_basic():
    with patch("streamtex.write.st.html") as mock_html:
        st_write(s.bold, "Hello")
        mock_html.assert_called_once()
        html = mock_html.call_args[0][0]
        assert "Hello" in html
        assert "font-weight" in html
```

### 2. Testing Style Composition

```python
def test_style_add():
    a = Style("color: red;", "a")
    b = Style("font-size: 16px;", "b")
    combined = a + b
    css = combined.css
    assert "color: red" in css
    assert "font-size: 16px" in css
```

### 3. Testing Context Managers (st_block, st_grid, st_list)

```python
def test_st_block_nesting():
    with patch("streamtex.container.st.html") as mock_html:
        with st_block(s.bold):
            st_write(s.large, "Inside")
        # Verify the block wrapper was rendered
        calls = mock_html.call_args_list
        # First call: block open, second: content, third: block close
```

### 4. AST Guard Pattern (`test_export_guard.py`)

This test scans all `streamtex/*.py` source files using Python's `ast` module to ensure no function calls `st.html()` directly except through the approved `_render()` pipeline. Add new whitelisted callers here if needed.

### 5. Testing Export Buffer

```python
def test_buffer_push_pop():
    config = ExportConfig(enabled=True)
    buf = HtmlExportBuffer(config)
    buf.push_wrapper("<div>")
    buf.append("<p>Hello</p>")
    buf.pop_wrapper("</div>")
    html = buf.get_html()
    assert "<div><p>Hello</p></div>" in html
```

## Writing New Tests

1. Create `tests/test_<module>.py` matching the source module name
2. Import the function under test from `streamtex`
3. Mock `st.html` (or `components.html` for JS-enabled features like marker)
4. Test both normal rendering and export buffer integration
5. Reset global state (TOC, markers) in setup/teardown if your test touches singletons
6. Run `uv run pytest tests/test_<module>.py -v` to verify
7. Run the full suite: `uv run pytest tests/ -v`

## Important Gotchas

- **Singleton state**: `toc.py` and `marker.py` accumulate state across calls. Always call `reset_toc_registry()` or equivalent in test setup.
- **`from streamtex import *`**: This shadows Python's `list()` builtin. In test code, use `[*iterable]` instead of `list(iterable)`.
- **`st.html()` vs `components.html()`**: Since Streamlit 1.54+, `st.html()` strips `<script>` tags. Features needing JS (marker, zoom) use `components.html()` instead.
- **Export buffer stack**: If a test opens a context manager but doesn't close it (exception in test), the buffer stack leaks. Use try/finally or pytest fixtures.
