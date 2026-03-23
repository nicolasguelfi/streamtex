# /stx-ce:compound — Capitalize learnings for future improvement

Arguments: $ARGUMENTS

## Options

- `--category <cat>` — Force a category (structure|style|content|process|pedagogy|assets|deployment|import)
- `--help` — Show stx-ce cheatsheet

## Description

Documents what was learned during the production cycle to make future work easier. Analyzes the context, extracts successful patterns and encountered problems, checks for duplicates in existing solutions, and writes a capitalization document.

Solutions are stored in `docs/solutions/<category>/` with frontmatter for searchability.

8 categories: structure, style, content, process, pedagogy, assets, deployment, import.

## Examples

- `/stx-ce:compound` — Capitalize from recent work
- `/stx-ce:compound --category style` — Force style category

## Required Readings

Before executing, read:
1. `.claude/ce/skills/ce-compound.md` — Full workflow
2. `docs/solutions/` — Existing solutions to check for duplicates

## Workflow

Execute the `ce-compound` skill. Write solution to docs/solutions/<category>/.
