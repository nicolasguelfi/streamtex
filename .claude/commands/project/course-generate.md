Generate book.py for a course from its blocks.csv.

## Arguments
- `$ARGUMENTS` — Course name (e.g. `gai4as`) or `--all` for all courses.

## Workflow

1. **Locate** the course directory:
   - `projects/convert_html_to_streamtex/courses/$ARGUMENTS/`

2. **Read blocks.csv** to understand the block list and order.

3. **Run the book generator**:
   - For a single course:
     ```bash
     uv run python projects/convert_html_to_streamtex/tools/book_generator.py projects/convert_html_to_streamtex/courses/$ARGUMENTS
     ```
   - For all courses:
     ```bash
     uv run python projects/convert_html_to_streamtex/tools/book_generator.py --all
     ```

4. **Verify** the generated book.py looks correct.

5. **Test** the course (if requested):
   ```bash
   uv run streamlit run projects/convert_html_to_streamtex/courses/$ARGUMENTS/book.py
   ```
