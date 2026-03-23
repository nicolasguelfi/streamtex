# Template: Plan Import

Import production plan — detailed execution plan for importing external sources into a StreamTeX project.

## Structure

```markdown
# Production Plan — Pathway A: IMPORT

## Metadata

| Field | Value |
|-------|-------|
| Project | <project name> |
| Profile | <design profile name> |
| Pathway | IMPORT |
| Planning mode | <auto / interactive> |
| Sources to import | <number> |
| Assess report ref | <assess report file or date> |
| Estimated effort | <low / medium / high> |

## Sources to Import

| # | Source | Import Method | Target Block(s) | Effort |
|---|--------|--------------|-----------------|--------|
| 1 | <source name> | <pandoc / manual / partial> | <block_name_1, block_name_2> | <low / medium / high> |
| 2 | <...> | <...> | <...> | <...> |

## Document Structure

### Skeleton

| Part | Section | Objective | Sources | Content Type | Detail Level | Blocks |
|------|---------|-----------|---------|-------------|-------------|--------|
| <Part 1: Title> | <Section 1.1> | <what this section achieves> | <source #s> | <text / code / mixed / visual> | <overview / detailed / reference> | <block_name_1, block_name_2> |
| | <Section 1.2> | <...> | <...> | <...> | <...> | <...> |
| <Part 2: Title> | <Section 2.1> | <...> | <...> | <...> | <...> | <...> |

### Skeleton Validation

- [ ] All sources are assigned to at least one section
- [ ] No orphan sections (every section has at least one block)
- [ ] Part progression is logical
- [ ] Estimated block count: <number>

## Design Choices

| Aspect | Choice |
|--------|--------|
| Theme | <StreamTeX theme name> |
| Color palette | <palette description or name> |
| Layouts | <single column / two column / tabs / mixed> |
| Typography | <default / custom font choices> |
| Asset types | <diagrams / screenshots / icons / code snippets / tables> |
| Conventions | <naming, styling, or structural conventions> |

## Execution Order

| Step | Action | Blocks Affected | Dependencies |
|------|--------|----------------|-------------|
| 1 | <action description> | <block name(s)> | <none / step #> |
| 2 | <...> | <...> | <...> |
| 3 | <...> | <...> | <...> |

## Pre-Production Checklist

- [ ] Project created (`stx project new` or `/stx-designer:init`)
- [ ] Source files accessible and readable
- [ ] Conversion tools available (pandoc, etc.)
- [ ] Design profile selected and configured
- [ ] book.py skeleton matches planned structure
- [ ] Assets directory prepared
- [ ] Dependencies resolved (images, bibliographies)

## Next Step

Proceed with `/stx-ce:produce` to execute this plan.
```
