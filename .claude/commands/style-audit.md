Audit the styles of a StreamTeX block for consistency and best practices.

Arguments: $ARGUMENTS (path to the block file to audit, or "all" to audit the entire project)

## Steps

1. **Read the target**: Read the specified block file(s). If "all", scan all `bck_*.py` files in the project's `blocks/` directory.
2. **Load references**: Read `documentation/streamtex_cheatsheet_en.md` and `custom/styles.py` for the project.
3. **Check for violations** — report each with file path and line number:

### Critical Issues
- [ ] **Raw HTML/CSS strings**: Any inline `"color: red"` or `st.markdown(..., unsafe_allow_html=True)` usage
- [ ] **Hardcoded black/white**: `color: #000000`, `color: black`, `background: white` etc. (should be theme-controlled)
- [ ] **Multiple st_write for inline text**: Two or more `st_write()` calls where content should flow inline — should use tuple args
- [ ] **Missing font size on links**: `link=` parameter used with a style that doesn't include font size when surrounding text is > 12pt

### Warnings
- [ ] **Duplicate style definitions**: Two styles in `BlockStyles` with identical CSS
- [ ] **Non-English style names**: Style names using French or other non-English words
- [ ] **Unused styles**: Styles defined in `BlockStyles` but never referenced in `build()`
- [ ] **Missing BlockStyles class**: Block file without a `BlockStyles` or `BStyles` class
- [ ] **Missing build() function**: Block file without a `build()` function
- [ ] **Raw st.* for content**: Using `st.write`, `st.markdown`, `st.image`, `st.columns` for content rendering

### Recommendations
- [ ] **Dark mode compatibility**: Styles that may break in dark mode
- [ ] **Style reuse opportunities**: Repeated style compositions that could be extracted to `BlockStyles`
- [ ] **Missing TOC entries**: Headings that should have `toc_lvl` but don't

4. **Summary**: Provide a summary with counts per category (critical/warning/recommendation) and specific fix suggestions.
