# Template: Assess Import

Import assessment report (pathway A) — defines requirements and import strategy for external sources.

## Structure

```markdown
# Assessment Report — Pathway A: IMPORT

## Metadata

| Field | Value |
|-------|-------|
| Date | <YYYY-MM-DD> |
| Target project | <project name> |
| Pathway | IMPORT |
| Collect report ref | <collect report file or date> |
| Sources selected | <number of sources to import> |

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

### Sources (R16-R18)

| Req | Description | Specification |
|-----|-------------|---------------|
| R16 | Source formats | <list of formats: PDF, HTML, DOCX, etc.> |
| R17 | Source languages | <natural languages present in sources> |
| R18 | Licensing / attribution | <license constraints, attribution requirements> |

## Sources Selected for Import

| Priority | Source | Format | Import Method | Target Section |
|----------|--------|--------|--------------|----------------|
| 1 | <source name> | <format> | <pandoc / manual / partial> | <target part or section> |
| 2 | <...> | <...> | <...> | <...> |

## Granularity Decisions

| Source | Granularity | Rationale |
|--------|------------|-----------|
| <source> | <1 block per source / 1 section per source / regroup multiple sources> | <why this granularity> |

## Fidelity Level

| Source | Fidelity | Notes |
|--------|----------|-------|
| <source> | <identical / adapted / restructured> | <what changes are expected> |

## Next Step

Proceed with `/stx-ce:plan` to build the import production plan.
```
