---
alwaysApply: true
---

# StreamTeX Project Rules

## Prime Directive
**You are a StreamTeX Expert.**
- You DO NOT write standard Streamlit code unless explicitly necessary for interactivity (widgets).
- You ALWAYS prioritize the `streamtex` library over standard `streamlit` functions.
- You reference `documentation/streamtex_cheatsheet_en.md` for syntax and `documentation/coding_standards.md` for standards.

## Active Rule Sets
- **Core Development Standards**: `.cursor/rules/streamtex/development/RULE.md` (ALWAYS ACTIVE)
- **Environment Setup**: `.cursor/rules/env-setup/RULE.md`

## Context Loading
Before generating code for a block, always read:
1. `documentation/streamtex_cheatsheet_en.md`
2. The target project's `book.py` (for structure)

For architectural reference, inspect `tests/test_project/` (comprehensive feature showcase) or `documentation/template_project/` (starter template).

## Workflows & Capabilities
### 1. New Feature / Text Description
**Context:** User provides a text description.
**Strategy:** Follow `.cursor/rules/streamtex/development/RULE.md` strictly to build from scratch.

### 2. HTML Migration (Google Docs)
**Context:** User pastes raw HTML (e.g., from Google Docs export).
**Action:**
- Load and carefully read `.cursor/rules/streamtex/html-migration/RULE.md`.
- Load and carefully read `.cursor/rules/streamtex/html-migration/color-fidelity/RULE.md` (color handling).
- If the target project has an `input/` folder with source HTML, use it as context.
**Goal:**
- Extract content and map it to StreamTeX primitives (style consolidation, image naming, helper functions for repeated patterns).
- After producing an initial complete block implementation, perform the **mandatory second-pass verification and refinement** described in the html-migration rule:
  - Re-read the source HTML from top to bottom.
  - Re-read the html-migration and color-fidelity rules.
  - Update and refine the block code so the reconstructed layout and colors match the original HTML as faithfully as possible.

### 3. Visual Reconstruction (Screenshots)
**Context:** User uploads an image/screenshot.
**Action:** Load rules from `.cursor/rules/streamtex/visual-reconstruction/RULE.md`.
**Goal:** Analyze visual hierarchy and reconstruct using `st_grid` and `st_block`.
