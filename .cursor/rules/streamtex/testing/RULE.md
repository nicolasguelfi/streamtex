---
alwaysApply: false
---

# StreamTeX Testing Guidelines

## Test Structure
Tests live in `tests/` at the project root. Configuration is in `pyproject.toml`.

```
tests/
  __init__.py
  conftest.py          # Shared fixtures (mock st.html, etc.)
  test_styles.py       # Style +/-, theme overrides, StyleGrid
  test_write.py        # st_write rendering
  test_toc.py          # TOCRegistry
  test_utils.py        # strip_html, generate_key, URL detection
  test_enums.py        # Tags, ListTypes
```

## Running Tests
```bash
pytest tests/ -v       # All tests, verbose
pytest tests/test_styles.py  # Single module
```

## Conventions

### Mocking Streamlit
All tests use the `mock_streamlit` fixture from `conftest.py` which patches `st.html` and `st.markdown`. This runs automatically (autouse=True).

### Test Organization
- Group tests by class: `class TestStyleGrid:`, `class TestColors:`
- Each test method tests ONE behavior
- Name tests descriptively: `test_style_add_combines_css`, `test_lvl_cycles_symbols`

### What to Test
- **Style system**: `+`, `-`, `__repr__` with theme, `StyleGrid.create`, `ListStyle.lvl`
- **Rendering**: Verify `st.html` is called with correct HTML content
- **Utilities**: Pure functions (strip_html, generate_key, URL detection)
- **ToC**: Registry entries, hierarchical numbering, anchor generation

### What NOT to Test
- Streamlit internal behavior (CSS selectors, DOM rendering)
- Visual appearance (that's manual QA)
- Third-party libraries

### Naming
- File: `test_[module_name].py`
- Class: `Test[Feature]`
- Method: `test_[behavior_under_test]`
