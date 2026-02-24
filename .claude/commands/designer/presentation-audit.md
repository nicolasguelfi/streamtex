Audit a StreamTeX presentation block for live projection compliance.

## Before Auditing

Read these files (mandatory):
1. `.claude/designer/ros_designer_default/skills/presentation-design-rules.md`
2. `.claude/designer/skills/visual-design-rules.md` (base rules)
3. The target project's `custom/styles.py`

## Target

Audit the block file specified by $ARGUMENTS. If no argument given, ask the user which block to audit.

## Audit Checklist

### CRITICAL (must fix before presenting)

1. **Font size — body text**: All body content uses `s.Large` (48pt) or above. `s.medium`, `s.big`, `s.large` on body = CRITICAL.
2. **Font size — titles**: Section titles use `s.Huge` (96pt) or project title styles. `s.Large` on main titles = CRITICAL.
3. **Keywords only**: No bullet exceeds 7 words. No section has more than 3 bullets.
4. **High contrast**: No `muted` or `subtle` color on body text (only on attribution/source).
5. **Image sizing**: No image below 400px width (except logos).

### ERROR (should fix)

6. **Generous spacing**: `st_space(size=3)` minimum between sections. Less = ERROR.
7. **One idea per section**: Sections with multiple unrelated concepts = ERROR.
8. **No helper boxes**: `show_explanation()`, `show_details()`, `show_code()` in presentation blocks = ERROR.
9. **Chart readability**: Chart labels/values below 20px font-size = ERROR.
10. **Visual first**: Sections with only text and no visual anchor = ERROR.

### WARNING (consider fixing)

11. **Spacing consistency**: Inconsistent spacing between similar elements = WARNING.
12. **Style reuse**: Repeated inline style compositions instead of `BlockStyles` class = WARNING.
13. **Attribution placement**: Source/footer text above `s.large` (32pt) = WARNING (too prominent).

### Structure checks (base rules)

14. **BlockStyles class**: Missing `BlockStyles` + `bs` alias = ERROR.
15. **build() function**: Missing `build()` function = ERROR.
16. **Imports**: Missing standard imports = WARNING.

## Output Format

```
# Presentation Audit: <filename>

## Summary
- CRITICAL: N issues
- ERROR: N issues
- WARNING: N issues

## CRITICAL Issues
### [C1] <rule name>
- **Line**: <line number>
- **Found**: <what's wrong>
- **Expected**: <what it should be>
- **Fix**: <specific fix instruction>

## ERROR Issues
### [E1] ...

## WARNING Issues
### [W1] ...

## Passed Checks
- [x] <check name>
```
