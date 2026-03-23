# /stx-ce:produce — Execute the production plan

Arguments: $ARGUMENTS

## Options

- `--from-plan <path>` — Use a specific plan file (default: latest in docs/plans/)
- `--no-deploy` — Skip deployment step
- `--help` — Show stx-ce cheatsheet

## Description

Executes the production plan item by item. For each item, the appropriate StreamTeX command is invoked:

- **Import items**: `/stx-import:html`, `/stx-import:marp`, or manual conversion
- **Improvement items**: `/stx-designer:update`, `/stx-designer:style-refactor`
- **Creation items**: `/stx-designer:block-new`, `/stx-designer:slide-new`

Each item is audited after production (`/stx-designer:audit --target`) and fixed if needed. A global audit runs at the end.

## Examples

- `/stx-ce:produce` — Execute latest plan
- `/stx-ce:produce --from-plan docs/plans/2026-03-22-001-import-mycourse-plan.md`
- `/stx-ce:produce --no-deploy` — Produce without deploying

## Required Readings

Before executing, read:
1. `.claude/ce/skills/ce-produce.md` — Full workflow
2. `docs/plans/` — The plan to execute
3. `.claude/references/streamtex_cheatsheet_en.md` — StreamTeX API reference

## Workflow

Execute the `ce-produce` skill. Track progress with task list. Run global audit at the end.
