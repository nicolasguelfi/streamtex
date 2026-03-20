# .claude/custom/ — User Customizations

This directory is for **your** personalized extensions. Files here are:
- **Never overwritten** by `stx claude update`
- **Preserved** across preset upgrades (`stx install --preset`)
- **Loaded by Claude Code** as part of the `.claude/` context

## How to use

| What | Where | Example |
|------|-------|---------|
| Extra coding rules | `custom/references/` | `project_conventions.md` |
| Custom skills | `custom/skills/` | `my_domain_knowledge.md` |
| Custom templates | `custom/templates/` | `my_template.md` |

## Custom slash commands

Custom commands go directly in `.claude/commands/` (not in `custom/commands/`),
because Claude Code only scans `.claude/commands/` for slash commands.
Files you add there are safe — `stx claude update` only overwrites files
declared in the profile manifest.

## Official vs. custom files

- `.claude/references/`, `.claude/developer/`, `.claude/designer/` → **read-only** (managed by StreamTeX)
- `.claude/custom/` → **yours** (never touched by StreamTeX)
