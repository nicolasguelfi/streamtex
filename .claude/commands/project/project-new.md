Initialize a new StreamTeX project from the template.

Arguments: $ARGUMENTS (project name, e.g. "project_mycoursename")

## Steps

1. **Read the template**: Read `documentation/template_project/` structure to understand the reference layout:
   - `documentation/template_project/book.py`
   - `documentation/template_project/setup.py`
   - `documentation/template_project/blocks/__init__.py`
   - `documentation/template_project/blocks/helpers.py`
   - `documentation/template_project/custom/styles.py`
   - `documentation/template_project/custom/themes.py`
   - `documentation/template_project/.streamlit/config.toml`

2. **Parse the project name**: Ensure it follows `project_[name]` convention. Adjust if needed.

3. **Create the project directory** under `projects/` with full structure:
   ```
   [project_name]/
     book.py
     setup.py
     blocks/
       __init__.py
       helpers.py
       bck_welcome.py
     custom/
       styles.py
       themes.py
     static/
       images/
     .streamlit/
       config.toml
   ```

4. **Configure each file**:
   - `book.py`: Import setup, import blocks, configure `st.set_page_config(layout="wide")`, create `TOCConfig`, call `st_book()` with explicit `banner=BannerConfig.full()` when `paginate=True`
   - `setup.py`: Standard PATH setup (copy from template)
   - `blocks/__init__.py`: ProjectBlockRegistry lazy loader (copy from template)
   - `blocks/helpers.py`: Block helper config with DI pattern (copy from template)
   - `blocks/bck_welcome.py`: Starter block with a title and placeholder content
   - `custom/styles.py`: Custom styles class inheriting from `StxStyles`, with example color and title styles
   - `custom/themes.py`: Empty theme dictionary ready for overrides
   - `.streamlit/config.toml`: With `enableStaticServing = true` and `layout = "wide"`

5. **Create placeholder directories**: Ensure `static/images/` exists (create a `.gitkeep` if empty).

6. **Validate**: Confirm the project can run:
   ```bash
   uv run streamlit run projects/[project_name]/book.py
   ```

7. **Show next steps** to the user:
   - How to add new blocks (`/designer:block-new`)
   - How to customize styles in `custom/styles.py`
   - How to configure block helpers in `blocks/helpers.py`
   - How to configure the table of contents in `book.py`

## Reference Projects
- `documentation/template_project/` — canonical template (source of truth)
- `documentation/manuals/stx_manual_intro/` — Phase 1 intro course example
- `documentation/manuals/stx_manual_advanced/` — Phase 1 advanced + multi-source blocks example
