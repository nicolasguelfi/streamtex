Upgrade a StreamTeX project to match the latest template: $ARGUMENTS

1. Read `documentation/template_project/` to understand the current template structure
2. Compare the target project's boilerplate files against the template:
   - `blocks/__init__.py`
   - `blocks/helpers.py`
   - `setup.py`
   - `.streamlit/config.toml`
3. Report differences and apply updates where safe
4. Do NOT modify `custom/styles.py` or `custom/themes.py` (these are project-specific)
5. Do NOT modify block content files
6. Run `uv run streamlit run <project>/book.py` in a dry check if possible
