Fix all visual design violations in a StreamTeX slide.

Arguments: $ARGUMENTS (file path or block name)

## Steps

1. **Run audit first**: Follow the audit process from `/designer:slide-audit` to identify all violations.
2. **Load rules**: Read `.claude/designer/skills/visual-design-rules.md`.
3. **Apply fixes** for each violation found:
   - **Long lines**: Break into `st_write()` + `st_br()` pattern
   - **Missing show_code()**: Add `show_code(textwrap.dedent("""\..."""))` before live rendering
   - **String concatenation**: Split into separate `st_write()` + `st_br()` calls
   - **Missing explanation**: Add `show_explanation(textwrap.dedent("""\..."""))`
   - **Missing defaults**: Add defaults info to `show_details()` section
   - **Wrong font size**: Replace `s.big` with `s.large` for body text
   - **Missing WRONG explanation**: Add `st_write()` + `st_br()` lines explaining WHY
   - **Old varargs pattern**: Convert to `textwrap.dedent("""\...""")`
4. **Verify**: Import the module to confirm no syntax errors.
5. **Report**: List all changes made.

## Constraints
- Only modify what violates the rules
- Preserve the existing content and structure
- Do not change style compositions unless they use wrong sizes
