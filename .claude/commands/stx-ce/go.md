# /stx-ce:go — Run the full CE cycle autonomously

Arguments: $ARGUMENTS

## Options

- `--quick` — Skip COLLECT + ASSESS, go directly to PLAN
- `--from-plan <path>` — Resume from an existing plan
- `--interactive` — Force interactive planning mode
- `--review-only` — Only run REVIEW on existing project
- `--no-deploy` — Skip deployment
- `--import <path>` — Force import pathway (A) with source path
- `--improve` — Force improvement pathway (B)
- `--help` — Show stx-ce cheatsheet

## Description

Executes the complete CE cycle (COLLECT > ASSESS > PLAN > PRODUCE > REVIEW > COMPOUND) with validation gates.

The planning mode is auto-detected: interactive if COLLECT finds >= 10 sources or >= 20 estimated blocks, auto otherwise. Use `--interactive` to force collaborative planning.

**Gates** (mandatory user validation):
1. After PLAN: user must approve the plan before production starts
2. After REVIEW: user must approve the review before capitalization

## Examples

- `/stx-ce:go Import my PowerPoint slides from ~/slides/` — Full cycle with import
- `/stx-ce:go --quick Create a course on design patterns` — Skip collect/assess
- `/stx-ce:go --improve` — Full cycle to improve current project
- `/stx-ce:go --from-plan docs/plans/2026-03-22-001-import-mycourse-plan.md`
- `/stx-ce:go --review-only` — Review existing project only

## Required Readings

Before executing, read:
1. `.claude/ce/skills/ce-go.md` — Full workflow

## Workflow

Execute the `ce-go` skill. Follow the sequential pipeline with gates.
