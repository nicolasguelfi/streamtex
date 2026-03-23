# Template: Plan Create

Creation production plan — detailed execution plan for building a new StreamTeX document from scratch.

## Structure

```markdown
# Production Plan — Pathway C: CREATION

## Metadata

| Field | Value |
|-------|-------|
| Project name | <project name> |
| Document type | <manual / presentation / course / report / collection> |
| Profile | <design profile name> |
| Template | <project / presentation / collection / course> |
| Planning mode | <auto / interactive> |
| Estimated blocks | <number> |
| Estimated parts | <number> |
| Assess report ref | <assess report file or date> |
| Context | <standalone / part of series / companion to X> |

## Document Structure

### Skeleton (validated)

| Part | Section | Objective | Sources | Content Type | Detail Level | Blocks |
|------|---------|-----------|---------|-------------|-------------|--------|
| <Part 1: Title> | <Section 1.1> | <what this section achieves> | <reference material, if any> | <text / code / mixed / visual> | <overview / detailed / reference> | <block_name_1, block_name_2> |
| | <Section 1.2> | <...> | <...> | <...> | <...> | <...> |
| <Part 2: Title> | <Section 2.1> | <...> | <...> | <...> | <...> | <...> |

### Skeleton Validation

- [ ] All requirements (R1-R15) are addressed by at least one section
- [ ] Part progression follows chosen narrative arc
- [ ] No empty parts or sections
- [ ] Estimated block count: <number>
- [ ] Complexity is appropriate for target audience

## Design Choices

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Theme | <StreamTeX theme name> | <why this theme> |
| Color palette | <palette description or name> | <why this palette> |
| Layouts | <single column / two column / tabs / mixed> | <why this layout> |
| Typography | <default / custom font choices> | <why this typography> |
| Asset types | <diagrams / screenshots / icons / code snippets / tables> | <why these assets> |
| Conventions | <naming, styling, or structural conventions> | <source of conventions> |

## Dependencies

### Assets

| Asset | Type | Status | Source |
|-------|------|--------|--------|
| <asset name> | <image / diagram / data file / icon> | <to create / exists / to acquire> | <where it comes from> |

### Prerequisite Blocks

| Block | Dependency | Type |
|-------|-----------|------|
| <block_name> | <other block or config> | <must exist before / shared asset / shared style> |

<If no dependencies: "No inter-block dependencies.">

### book.py Configuration

| Config Item | Value | Notes |
|-------------|-------|-------|
| Title | <document title> | |
| Theme | <theme name> | |
| Custom settings | <any st_book kwargs> | |

### Coherence with Existing Documents

| Document | Coherence Point | Action Required |
|----------|----------------|----------------|
| <existing document> | <shared terminology / shared style / cross-reference> | <what to ensure> |

<If standalone: "No coherence constraints — standalone document.">

## Pre-Production Checklist

- [ ] Project created (`stx project new` or `/stx-designer:init`)
- [ ] Design profile selected and configured
- [ ] book.py initialized with skeleton structure
- [ ] blocks/ directory created
- [ ] Assets directory prepared
- [ ] Reference materials accessible
- [ ] Conventions documented or profile applied

## Next Step

Proceed with `/stx-ce:produce` to execute this plan.
```
