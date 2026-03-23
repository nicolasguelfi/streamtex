# /stx-ce:collect — Inventory and classify existing material

Arguments: $ARGUMENTS

## Options

- `<path>` — Path to a directory of source files to scan
- `--project <name>` — Analyze an existing StreamTeX project
- `--url <url>` — Fetch and analyze web content
- `--help` — Show stx-ce cheatsheet

## Description

Scans source material (documents, presentations, images, code, existing StreamTeX projects) and produces an inventory report with import recommendations. This is the starting point of the CE cycle for most users.

Supported source types: .docx, .pptx, .pdf, .tex, .md, .html, .py (StreamTeX), images, videos.

## Examples

- `/stx-ce:collect ~/courses/info101/` — Scan a course folder
- `/stx-ce:collect --project stx-ai4se` — Analyze existing project
- `/stx-ce:collect ~/slides/ ~/notes/` — Scan multiple paths

## Required Readings

Before executing, read:
1. `.claude/ce/skills/ce-collect.md` — Full workflow
2. `.claude/skills/import-conventions.md` — Import rules (if sources detected)

## Workflow

Execute the `ce-collect` skill with the provided arguments. Generate the report in `docs/collect/`.
