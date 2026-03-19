# StreamTeX Documentation Lookup

Reference skill for finding examples, patterns, and answers in the StreamTeX manuals.

## Manual Locations

The documentation lives in `streamtex-docs/manuals/` relative to the workspace root.
From a project, the typical path is `../../streamtex-docs/manuals/` or `../streamtex-docs/manuals/`.

## Manual Index

| Manual | Path | Topics | Blocks |
|--------|------|--------|--------|
| Intro | `stx_manual_intro/blocks/` | Text, grids, lists, images, containers, styles, installation | ~29 |
| Advanced | `stx_manual_advanced/blocks/` | Export, PDF, bibliography, diagrams, overlays, banners, visibility | ~48 |
| AI | `stx_manual_ai/blocks/` | AI image generation, providers, caching, Claude profiles, prompts | ~40 |
| Deploy | `stx_manual_deploy/blocks/` | Docker, Render, CI/CD, preflight checks | ~12 |
| Developer | `stx_manual_developer/blocks/` | Architecture, block system, testing, CLI, migration | ~41 |
| Collection | `stx_manuals_collection/blocks/` | Multi-project hubs | ~1 |

## Block File Structure

Each block file (`bck_*.py`) follows this pattern:
```
blocks/
├── bck_topic.py              # Composite block (includes atomic blocks)
└── _atomic/
    ├── bck_topic_part1.py    # Atomic block with live examples
    └── bck_topic_part2.py
```

Inside each atomic block:
- `class BlockStyles` — styles used in the block
- `def build()` — the main content with:
  - `show_explanation("...")` — explanatory text
  - `show_code("...")` — code examples (Python snippets users can copy)
  - `show_details("...")` — expandable details/tips
  - Live rendering: `st_write()`, `st_grid()`, `st_list()`, etc.

## Search Strategy

When looking for an answer:

1. **Identify the topic category**:
   - Text/styling/layout → Intro manual
   - Grids, lists, containers → Intro manual
   - Export, PDF, bibliography, diagrams → Advanced manual
   - AI images, Claude → AI manual
   - Docker, Render, CI → Deploy manual
   - Testing, architecture, CLI → Developer manual

2. **Search block filenames** — they are descriptive:
   - `bck_grids_and_lists.py`, `bck_text_styles.py`, `bck_containers.py`
   - `bck_export_html.py`, `bck_pdf_export.py`, `bck_bibliography_references.py`
   - `bck_ai_image_overview.py`, `bck_ai_image_usage.py`
   - Use glob: `../../streamtex-docs/manuals/stx_manual_*/blocks/**/bck_*<keyword>*.py`

3. **Read the block** — focus on `show_code()` strings for copy-paste examples.

4. **Check `book.py`** in each manual for the TOC/block ordering.

## When Manuals Are NOT Available

If the path `../../streamtex-docs/manuals/` does not exist, the user has a `basic` or `user` preset.

Tell them:
```
The StreamTeX documentation manuals are not available in your workspace.
To access 114+ example blocks with live code examples:

  stx install --preset standard
  stx update

This clones streamtex-docs with 6 manuals covering all StreamTeX features.
```

Then fall back to:
1. `.claude/references/streamtex_cheatsheet_en.md` — API reference
2. `.claude/references/coding_standards.md` — patterns and rules
3. Your own knowledge of the StreamTeX API

## Common Lookup Patterns

| User question | Search in | Block hint |
|---------------|-----------|------------|
| "How to make a grid?" | Intro | `bck_grids_and_lists`, `bck_grid_cell_styles` |
| "How to style text?" | Intro | `bck_text_styles`, `bck_text_and_styles` |
| "How to make a list?" | Intro | `bck_list_styles`, `bck_grids_and_lists` |
| "How to add images?" | Intro | `bck_images` |
| "How to export HTML?" | Advanced | `bck_export_html`, `bck_export_advanced` |
| "How to export PDF?" | Advanced | `bck_pdf_export` |
| "How to add bibliography?" | Advanced | `bck_bibliography_references` |
| "How to use Mermaid?" | Advanced | `bck_mermaid_diagrams` |
| "How to generate AI images?" | AI | `bck_ai_image_overview`, `bck_ai_image_usage` |
| "How to configure the banner?" | Advanced | `bck_banner_config` |
| "How to use overlays?" | Advanced | `bck_overlays` |
| "How to test blocks?" | Developer | `bck_dev_testing`, `bck_testing_gotchas` |
| "How to deploy to Render?" | Deploy | `bck_render` |
| "How to set up CI?" | Deploy | `bck_ci_cd` |
