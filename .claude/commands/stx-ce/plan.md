# /stx-ce:plan — Plan document production

Arguments: $ARGUMENTS

## Options

- `--interactive` — Enable 4-step collaborative planning (skeleton > objectives > design > plan)
- `--deep` — Run all agents in parallel for comprehensive research before planning
- `--help` — Show stx-ce cheatsheet

## Description

Creates a structured production plan from the assessment. Supports two modes:

- **Auto** (default): Generates the plan in a single pass. Best for small documents or simple improvements.
- **Interactive** (`--interactive`): 4-step collaborative planning where the user validates each layer (skeleton, per-section objectives, design choices, final plan). Best for complex documents.

The plan varies by pathway (import/improve/create) and includes: document skeleton, per-section objectives, design choices, execution order, and pre-production checklist.

## Examples

- `/stx-ce:plan` — Auto mode from latest assessment
- `/stx-ce:plan --interactive` — Collaborative 4-step planning
- `/stx-ce:plan --interactive --deep` — Deep research + interactive planning

## Required Readings

Before executing, read:
1. `.claude/ce/skills/ce-plan.md` — Full workflow
2. `docs/assess/` — Latest assessment document
3. `.claude/designer/skills/block-blueprints.md` — Block catalog for structure planning
4. `.claude/designer/templates/` — Available project templates

## Workflow

Execute the `ce-plan` skill. GATE: The plan must be validated by the user before proceeding to production.
