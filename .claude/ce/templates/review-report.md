# Template: Review Report

Multi-perspective review report — consolidates findings from all review agents into an actionable improvement plan.

## Structure

```markdown
# Review Report

## Metadata

| Field | Value |
|-------|-------|
| Date | <YYYY-MM-DD> |
| Project | <project name> |
| Plan reference | <plan file or date> |
| Assess reference | <assess file or date> |
| Reviewers | <list of perspectives activated> |

## Summary

| Perspective | Agent | CRITICAL | MAJOR | MINOR | SUGGESTION |
|------------|-------|----------|-------|-------|------------|
| Audience / Learner | <agent name> | <n> | <n> | <n> | <n> |
| Pedagogical Design | <agent name> | <n> | <n> | <n> | <n> |
| Visual Design | <agent name> | <n> | <n> | <n> | <n> |
| Technical Coherence | <agent name> | <n> | <n> | <n> | <n> |
| Editorial | <agent name> | <n> | <n> | <n> | <n> |
| **Total** | | **<n>** | **<n>** | **<n>** | **<n>** |

## Findings by Perspective

### Audience / Learner

| # | Severity | Description | Block(s) Affected | Suggested Fix |
|---|----------|-------------|-------------------|---------------|
| 1 | <CRITICAL / MAJOR / MINOR / SUGGESTION> | <finding description> | <block_name(s)> | <fix command or manual action> |
| 2 | <...> | <...> | <...> | <...> |

### Pedagogical Design

| # | Severity | Description | Block(s) Affected | Suggested Fix |
|---|----------|-------------|-------------------|---------------|
| 1 | <CRITICAL / MAJOR / MINOR / SUGGESTION> | <finding description> | <block_name(s)> | <fix command or manual action> |
| 2 | <...> | <...> | <...> | <...> |

### Visual Design

| # | Severity | Description | Block(s) Affected | Suggested Fix |
|---|----------|-------------|-------------------|---------------|
| 1 | <CRITICAL / MAJOR / MINOR / SUGGESTION> | <finding description> | <block_name(s)> | <fix command or manual action> |
| 2 | <...> | <...> | <...> | <...> |

### Technical Coherence

| # | Severity | Description | Block(s) Affected | Suggested Fix |
|---|----------|-------------|-------------------|---------------|
| 1 | <CRITICAL / MAJOR / MINOR / SUGGESTION> | <finding description> | <block_name(s)> | <fix command or manual action> |
| 2 | <...> | <...> | <...> | <...> |

### Editorial

| # | Severity | Description | Block(s) Affected | Suggested Fix |
|---|----------|-------------|-------------------|---------------|
| 1 | <CRITICAL / MAJOR / MINOR / SUGGESTION> | <finding description> | <block_name(s)> | <fix command or manual action> |
| 2 | <...> | <...> | <...> | <...> |

## Cross-Perspective Synthesis

### Contradictions

| Perspective A | Finding | Perspective B | Finding | Resolution |
|--------------|---------|--------------|---------|------------|
| <perspective> | <finding #> | <perspective> | <finding #> | <how to resolve the contradiction> |

<If no contradictions: "No contradictions detected between perspectives.">

### Priorities

<Summary of the most impactful findings across all perspectives, ranked by combined severity and scope.>

## Action Plan

| # | Finding Ref | Severity | Fix Method | Automatable? |
|---|------------|----------|-----------|-------------|
| 1 | <perspective + finding #> | <CRITICAL / MAJOR / MINOR> | <manual edit / /stx-designer:fix / /stx-designer:update / code change> | <yes / no / partial> |
| 2 | <...> | <...> | <...> | <...> |

## Next Step

- For automatable fixes: proceed with `/stx-designer:fix`
- For all other items: proceed with `/stx-ce:compound` to apply fixes and capitalize learnings
```
