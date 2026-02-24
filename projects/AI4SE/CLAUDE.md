# AI4SE Project — Claude Code Rules

## Design Role

This project uses the **`ros_designer_default`** presentation design role.

All slides in this project are designed for **live projection at 10–20 m distance**.

### Mandatory Reading (before any block creation or modification)

1. `.claude/designer/ros_designer_default/skills/presentation-design-rules.md` — 9 rules
2. `.claude/designer/ros_designer_default/agents/presentation-designer.md` — agent role
3. `.claude/designer/skills/visual-design-rules.md` — base rules (overridden where conflicts)
4. `.claude/designer/skills/style-conventions.md` — style patterns
5. This file — project-specific context

### Key Overrides (vs base StreamTeX rules)

| Aspect | Base rule | Presentation override |
|---|---|---|
| Body font | `s.large` (32pt) | `s.Large` (48pt) minimum |
| Course title | `s.Giant` (128pt) | `s.Huge` (96pt) — Giant is exceptional only |
| Section titles | `s.Large` (48pt) | `s.huge` (80pt) or `s.Huge` (96pt) |
| Content density | ~45 chars/line | 5–7 words/bullet, 3 bullets max |
| Spacing | `st_space(size=2)` | `st_space(size=3)` between sections |
| Helper boxes | Required pattern | **Forbidden** — direct `st_write()` only |
| Body colors | Any palette color | No `muted`/`subtle` on body |
| Giant/GIANT | Title size | **Exceptional only** — single-word decorative elements |

### Commands

- `/designer:presentation-audit <block_file>` — check block for compliance
- `/designer:presentation-fix <block_file>` — auto-fix violations
- `/designer:survey-convert <image_or_--all>` — convert SO survey screenshot to block

## Project Context

- **Course**: AI4SE — Generative Software Engineering
- **Venue**: Digital Learning Hub, Luxembourg
- **Audience**: Seated at 10–20 m from projection screen
- **Theme**: Dark-mode-first with AI/tech aesthetic (`custom/styles.py`)

## Project Paths

| Resource | Path (relative to project root) |
|---|---|
| Source images (screenshots to convert) | `temp/` |
| Static images (served by Streamlit) | `static/images/` |
| Block files | `blocks/` |
| Block registry | `blocks/__init__.py` |
| Book orchestration | `book.py` |
