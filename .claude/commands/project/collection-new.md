Initialize a new StreamTeX collection (multi-project hub) from the template.

Arguments: $ARGUMENTS (collection name, e.g. "my_course_library")

## Steps

1. **Read the template**: Read `documentation/template_collection/` structure to understand the reference layout:
   - `documentation/template_collection/book.py`
   - `documentation/template_collection/setup.py`
   - `documentation/template_collection/collection.toml`
   - `documentation/template_collection/blocks/__init__.py`
   - `documentation/template_collection/blocks/helpers.py`
   - `documentation/template_collection/blocks/bck_home.py`
   - `documentation/template_collection/custom/styles.py`
   - `documentation/template_collection/custom/themes.py`
   - `documentation/template_collection/.streamlit/config.toml`

2. **Parse the collection name**: Ensure it follows a clean naming convention. Prefix with `collection_` if needed.

3. **Create the collection directory** under `projects/` with full structure:
   ```
   [collection_name]/
     book.py
     setup.py
     collection.toml
     blocks/
       __init__.py
       helpers.py
       bck_home.py
     custom/
       styles.py
       themes.py
     static/
       images/
         covers/
     .streamlit/
       config.toml
   ```

4. **Configure each file**:
   - `book.py`: Import `st_collection`, `CollectionConfig`, load from `collection.toml`, apply theme
   - `setup.py`: Standard PATH setup (copy from template)
   - `collection.toml`: Configure collection title, description, and placeholder project entries
   - `blocks/__init__.py`: ProjectBlockRegistry lazy loader (copy from template)
   - `blocks/helpers.py`: Block helper config (copy from template)
   - `blocks/bck_home.py`: Home page block with project cards (copy from template, customize)
   - `custom/styles.py`: Custom styles class (copy from template)
   - `custom/themes.py`: Dark/light theme dictionaries (copy from template)
   - `.streamlit/config.toml`: Dark theme config with colors

5. **Create placeholder directories**: Ensure `static/images/covers/` exists.

6. **Ask the user** about their projects:
   - How many projects will be in the collection?
   - What are their names, descriptions, and ports?
   - Update `collection.toml` accordingly

7. **Validate**: Confirm the collection can run:
   ```bash
   uv run streamlit run projects/[collection_name]/book.py
   ```

8. **Show next steps**:
   - How to add more projects to `collection.toml`
   - How to customize the home page in `blocks/bck_home.py`
   - How to run individual projects on different ports: `uv run streamlit run <project>/book.py --server.port 8502`
   - How to use `./run-test-projects.sh` for running multiple projects simultaneously

## Reference Projects
- `documentation/template_collection/` — canonical template (source of truth)
- `documentation/manuals/stx_manuals_collection/` — working collection example
