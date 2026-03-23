# Template: Assess Improve

Improvement assessment report (pathway B) — evaluates current document state and identifies gaps to address.

## Structure

```markdown
# Assessment Report — Pathway B: IMPROVEMENT

## Metadata

| Field | Value |
|-------|-------|
| Date | <YYYY-MM-DD> |
| Project name | <project name> |
| Pathway | IMPROVEMENT |
| Current blocks | <number of blocks> |
| Current parts | <number of parts> |
| Audit findings summary | <number of CRITICAL / MAJOR / MINOR issues> |

## Current State

| Metric | Value |
|--------|-------|
| Total blocks | <number> |
| Total parts | <number> |
| Last audit date | <YYYY-MM-DD or "none"> |
| Known issues | <brief summary> |

## Requirements

### Identity (R1-R4)

| Req | Description | Specification |
|-----|-------------|---------------|
| R1 | Document title | <title> |
| R2 | Author(s) | <author list> |
| R3 | Target audience | <audience description> |
| R4 | Document purpose | <purpose statement> |

### Content (R5-R8)

| Req | Description | Specification |
|-----|-------------|---------------|
| R5 | Subject scope | <topics covered> |
| R6 | Depth level | <introductory / intermediate / advanced> |
| R7 | Prerequisites | <required knowledge> |
| R8 | Learning objectives | <what the reader will learn> |

### Form (R9-R12)

| Req | Description | Specification |
|-----|-------------|---------------|
| R9 | Document type | <manual / presentation / course / report / collection> |
| R10 | Estimated length | <number of parts, sections, blocks> |
| R11 | Visual style | <theme, palette, conventions> |
| R12 | Interactivity level | <static / interactive widgets / exercises> |

### Delivery (R13-R15)

| Req | Description | Specification |
|-----|-------------|---------------|
| R13 | Delivery format | <web / PDF / both> |
| R14 | Deployment target | <local / Render / Hetzner / other> |
| R15 | Update frequency | <one-shot / periodic / continuous> |

## Gaps Identified

### Content Gaps

| # | Gap Description | Affected Section | Severity |
|---|----------------|-----------------|----------|
| 1 | <missing topic, outdated content, incomplete explanation> | <part / section> | <CRITICAL / MAJOR / MINOR> |

### Style Gaps

| # | Gap Description | Affected Block(s) | Severity |
|---|----------------|-------------------|----------|
| 1 | <inconsistent styling, wrong theme, accessibility issue> | <block name(s)> | <CRITICAL / MAJOR / MINOR> |

### Structure Gaps

| # | Gap Description | Affected Area | Severity |
|---|----------------|--------------|----------|
| 1 | <wrong order, missing part, unbalanced sections> | <area> | <CRITICAL / MAJOR / MINOR> |

## Improvements Prioritized

| # | Area | Type | Priority | Description |
|---|------|------|----------|-------------|
| 1 | <content / style / structure> | <add / revise / remove / reorganize> | <P1 / P2 / P3> | <what to do> |
| 2 | <...> | <...> | <...> | <...> |

## External Sources to Integrate

<If pathway A+B:>

| Source | Purpose | Import Method |
|--------|---------|--------------|
| <source name> | <what it adds to the document> | <pandoc / manual / partial> |

<If pure B: "No external sources — improvement only.">

## Next Step

Proceed with `/stx-ce:plan` to build the improvement production plan.
```
