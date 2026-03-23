# Template: Plan Improve

Improvement production plan — detailed execution plan for enhancing an existing StreamTeX document.

## Structure

```markdown
# Production Plan — Pathway B: IMPROVEMENT

## Metadata

| Field | Value |
|-------|-------|
| Project | <project name> |
| Pathway | IMPROVEMENT |
| Planning mode | <auto / interactive> |
| Current state | <number of blocks, parts> |
| Audit findings | <CRITICAL: n, MAJOR: n, MINOR: n> |
| Assess report ref | <assess report file or date> |
| Estimated effort | <low / medium / high> |

## Improvements

| # | Block | Action | Type | Reason | Effort |
|---|-------|--------|------|--------|--------|
| 1 | <block_name> | <revise / rewrite / split / merge / add / remove / restyle> | <content / style / structure> | <gap or issue reference> | <low / medium / high> |
| 2 | <...> | <...> | <...> | <...> | <...> |

## Document Structure

### Skeleton (validated)

| Part | Section | Objective | Changes | Blocks |
|------|---------|-----------|---------|--------|
| <Part 1: Title> | <Section 1.1> | <what this section achieves> | <new / revised / unchanged> | <block_name_1, block_name_2> |
| | <Section 1.2> | <...> | <...> | <...> |
| <Part 2: Title> | <Section 2.1> | <...> | <...> | <...> |

### Skeleton Validation

- [ ] All improvements are mapped to specific blocks
- [ ] No structural regressions introduced
- [ ] Part progression remains logical
- [ ] Block count after improvements: <number>

## Design Choices

| Aspect | Current | Revised | Rationale |
|--------|---------|---------|-----------|
| Theme | <current> | <revised or "unchanged"> | <why> |
| Color palette | <current> | <revised or "unchanged"> | <why> |
| Layouts | <current> | <revised or "unchanged"> | <why> |
| Typography | <current> | <revised or "unchanged"> | <why> |
| Asset types | <current> | <revised or "unchanged"> | <why> |

## External Sources to Integrate

<If pathway A+B:>

| Source | Purpose | Import Method | Target Block(s) |
|--------|---------|--------------|-----------------|
| <source name> | <what it adds> | <pandoc / manual / partial> | <block name(s)> |

<If pure B: "No external sources — improvement only.">

## Execution Order

| Step | Action | Blocks Affected | Dependencies |
|------|--------|----------------|-------------|
| 1 | <action description> | <block name(s)> | <none / step #> |
| 2 | <...> | <...> | <...> |
| 3 | <...> | <...> | <...> |

## Pre-Production Checklist

- [ ] Current document backed up or committed
- [ ] Audit report reviewed and findings confirmed
- [ ] Design changes validated against profile
- [ ] book.py skeleton updated to reflect structural changes
- [ ] New assets prepared (if any)
- [ ] External sources accessible (if pathway A+B)
- [ ] No conflicting edits in progress

## Next Step

Proceed with `/stx-ce:produce` to execute this plan.
```
