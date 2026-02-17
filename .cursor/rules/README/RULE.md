---
alwaysApply: false
---

# Cursor Rules Organization

This directory contains the rules that guide the Cursor AI agent.

## Structure
- **streamtex/development/RULE.md**: Core development guidelines for writing StreamTeX code.
- **streamtex/html-migration/RULE.md**: Rules for migrating HTML content to StreamTeX blocks.
- **streamtex/html-migration/color-fidelity/RULE.md**: Color fidelity rules during HTML migration.
- **streamtex/testing/RULE.md**: Testing conventions and patterns.

## Shared Standards
All coding standards are maintained in `documentation/coding_standards.md` (single source of truth).
Rules in this directory reference that file rather than duplicating content.

## Adding New Rules
1. Create a `RULE.md` file in the appropriate subdirectory.
2. Use `alwaysApply: true` for rules that should always be active.
