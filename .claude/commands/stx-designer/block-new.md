Create a new StreamTeX block file.

Arguments: $ARGUMENTS (block name and optional description, e.g. "bck_intro_welcome - Welcome screen with title and subtitle")

## Steps

1. **Load context**: Read `documentation/streamtex_cheatsheet_en.md` for syntax reference.
2. **Read architecture**: Read the target project's `book.py` to understand how blocks are wired. For reference, see `documentation/template_project/book.py` or `documentation/manuals/stx_manual_intro/book.py`.
3. **Check blueprints**: Read `.claude/designer/skills/block-blueprints.md` and check if a blueprint matches the requested block type. If a match is found, use it as the structural base and adapt it to the user's specific context (subject, palette, audience). Common matches:
   - "title slide" → Blueprint 1 (bck_title)
   - "comparison X vs Y" → Blueprint 4 (bck_comparison)
   - "code demo" → Blueprint 6 (bck_code_demo)
   - "steps / process" → Blueprint 7 (bck_timeline)
   - "summary / conclusion" → Blueprint 10 (bck_conclusion)
4. **Parse arguments**: Extract the block name (must follow `bck_[description]_[suffix]` format). If only a description is given, generate an appropriate name.
5. **Determine target project**: Look at the current working directory or ask the user which project to use.
6. **Create the block file** in `[project]/blocks/` with:
   - Standard mandatory imports (streamtex, styles, enums, custom.styles)
   - Import helpers from `blocks.helpers` (show_code, show_explanation, show_details)
   - A `BlockStyles` class with relevant styles for the described content
   - A `build()` function implementing the described content using `stx.*` functions
   - Proper TOC entries if the block has headings
7. **Update `blocks/__init__.py`**: Add the new module to the dynamic import list if it uses explicit imports (not needed with `ProjectBlockRegistry` lazy loader).
8. **Show wiring instructions**: Tell the user how to add the block to `book.py`:
   ```python
   import blocks
   # Add to the module list in st_book():
   st_book([..., blocks.bck_new_block_name], toc_config=toc)
   ```
9. **Validate**: Check that all referenced styles exist and all image URIs point to existing files.

## Constraints
- Follow ALL rules from CLAUDE.md
- No raw HTML/CSS strings
- Use English-only style names
- Block must have a `build()` function
- Use `stx.*` functions, never raw `st.*` for content
