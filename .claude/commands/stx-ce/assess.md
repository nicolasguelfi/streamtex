# /stx-ce:assess — Evaluate material and define document objectives

Arguments: $ARGUMENTS

## Options

- `--import` — Force import pathway (A)
- `--improve` — Force improvement pathway (B)
- `--create` — Force creation pathway (C)
- `--help` — Show stx-ce cheatsheet

## Description

Evaluates the current state (collected sources, existing project, or empty context) and defines what the target document should be. Auto-detects the appropriate pathway (A: import, B: improve, C: create) or accepts a forced pathway.

Produces a requirements document with audience profile, content objectives, and design preferences.

## Examples

- `/stx-ce:assess` — Auto-detect pathway from context
- `/stx-ce:assess --import` — Force import pathway
- `/stx-ce:assess Description of a new AI course` — Provide context for creation

## Required Readings

Before executing, read:
1. `.claude/ce/skills/ce-assess.md` — Full workflow
2. `docs/collect/` — Latest collect report (if exists)

## Workflow

Execute the `ce-assess` skill. Auto-detect pathway or use forced flag. Generate assessment in `docs/assess/`.
