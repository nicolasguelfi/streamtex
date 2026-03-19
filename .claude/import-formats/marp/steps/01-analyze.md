# Step 1 — Analyze Marp Source

> **Profile-aware:** Read the active profile from `.claude/import-formats/marp/profiles/{profile}.md`
> before generating the report. Include the profile name in the output.

## Workflow

1. **Scan** the source directory for `.md` files in `slides/` and `slots/`
2. **Extract** YAML frontmatter from each file (title, theme, size, paginate)
3. **Count slides** by counting `---` separators
4. **Inventory images** by finding `![...](...)` references
5. **Detect Marp classes** (`<!-- _class: lead/invert/small -->`)
6. **Detect** CSS theme file (usually in `slides/themes/`)
7. **Map** each source file to target StreamTeX block(s)
8. **Generate report** with:
   - Active profile name and key characteristics
   - Total files, slides, images
   - Per-file breakdown (slide count, images, classes used)
   - Suggested block naming and ordering
   - Missing images list

## Output Format

Markdown report printed to the user (not saved to file).

## Rules

- Read-only — does not modify any files
- Reports both `slides/` and `slots/` content
- Flags large files (>50 slides) that should be split into multiple blocks
- **Ask user for confirmation** before proceeding to step 2
