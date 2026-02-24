Fix all presentation design violations in a StreamTeX block for live projection.

## Before Fixing

Read these files (mandatory):
1. `.claude/designer/ros_designer_default/skills/presentation-design-rules.md`
2. `.claude/designer/skills/visual-design-rules.md` (base rules)
3. `.claude/designer/skills/style-conventions.md`
4. The target project's `custom/styles.py`

## Target

Fix the block file specified by $ARGUMENTS. If no argument given, ask the user which block to fix.

## Fix Catalog

Apply these transformations in order:

### 1. Small Body Fonts → `s.Large` (48pt)
- `s.medium` → `s.Large`
- `s.big` → `s.Large`
- `s.large` (when used as body) → `s.Large`

### 2. Small Title Fonts → `s.Huge` (96pt)+
- `s.Large` on main titles → `s.Huge` or project title style
- `s.large` on titles → `s.Huge`

### 3. Long Text → Keywords
- Sentences → 5–7 word keyword phrases
- Paragraphs → 3 keyword bullets max

### 4. Muted/Subtle Body → Primary/Accent
- `s.project.colors.muted` on body → remove or use `s.project.colors.accent`
- `s.project.colors.subtle` on body → remove or use primary color
- Keep muted/subtle on attribution/source/footer lines only

### 5. Insufficient Spacing → Generous
- `st_space(size=1)` between sections → `st_space(size=3)` or `st_space(size=4)`
- `st_space(size=2)` between sections → `st_space(size=3)` minimum

### 6. Helper Boxes → Direct Content
- `show_explanation(...)` → `st_write(bs.body, ...)`
- `show_details(...)` → remove or convert to keyword bullets
- `show_code(...)` → remove (not for presentation slides)

### 7. Small Images → 400px+
- `width="200px"` or similar → `width="600px"` (or appropriate large size)
- Keep logos at their designed size

### 8. Chart CSS → Readable Sizes
- Font sizes below 20px in `st.html()` chart CSS → 24px+
- Bar heights too small → increase

### 9. Missing BlockStyles Roles
- Ensure `heading`, `sub`, `body` exist in `BlockStyles`
- Add `body_accent` and `caption` if needed

### 10. Raw CSS in Content → Style Composition
- Inline CSS strings → `Style()` constructor or project palette styles

### 11. Dense Content → Split
- More than 3 bullets → split across sections or remove least important

## Workflow

1. Run `/presentation-audit` mentally to identify all violations
2. Apply fixes from this catalog, highest severity first
3. Verify the block still renders correctly (imports, syntax)
4. Report all changes made with before/after comparisons
