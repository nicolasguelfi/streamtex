---
alwaysApply: true
---
# Environment & Execution

## Shell Configuration
This project uses **uv** for dependency management. Never call `python`, `pip`, `pytest`, `streamlit`, or `ruff` directly.

1. **Install dependencies:**
```bash
uv sync
```

2. **Run a project:**
```bash
uv run streamlit run projects/<your_project>/book.py
```

3. **Run the test project:**
```bash
uv run streamlit run documentation/manuals/stx_manual_intro/book.py
```

4. **Run unit tests:**
```bash
uv run pytest tests/ -v
```

## Dependencies
- If import errors occur, run `uv sync` to install from `pyproject.toml` / `uv.lock`.
- Use `uv add <package>` to add dependencies, `uv add --group dev <package>` for dev deps.
- The `streamtex` package is installed in editable mode via `uv sync`.
