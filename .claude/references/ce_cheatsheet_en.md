# StreamTeX CE — Compound Document Engineering Quick Reference

## Cycle

```
COLLECT -> ASSESS -> PLAN -> PRODUCE -> REVIEW -> COMPOUND
   ^                  |                    |          |
   |               [GATE]              [GATE]         |
   +--------------------------------------------------+
```

## Commands

| Command | Description |
|---------|-------------|
| `/stx-ce:collect <path>` | Inventory and classify existing material |
| `/stx-ce:assess` | Evaluate material and define document objectives |
| `/stx-ce:plan [--interactive]` | Plan production (auto or collaborative 4-step) |
| `/stx-ce:produce` | Execute the plan (import/create/improve) |
| `/stx-ce:review [--fix]` | Multi-perspective review (5 agents) |
| `/stx-ce:compound` | Capitalize learnings in docs/solutions/ |
| `/stx-ce:go [flags]` | Full autonomous cycle with gates |

## Pathways

| Pathway | Starting point | Description |
|---------|---------------|-------------|
| **A (Import)** | External material (Word, PPT, PDF, LaTeX, HTML...) | Progressive import into StreamTeX |
| **B (Improve)** | Existing StreamTeX project | Correct, enrich, restructure |
| **C (Create)** | Context (other projects, collection) | New document in existing context |

## /stx-ce:go Flags

| Flag | Effect |
|------|--------|
| `--quick` | Skip COLLECT + ASSESS, go to PLAN |
| `--from-plan <path>` | Resume from existing plan |
| `--interactive` | Force 4-step collaborative planning |
| `--review-only` | Only REVIEW existing project |
| `--no-deploy` | Skip deployment |
| `--import <path>` | Force pathway A |
| `--improve` | Force pathway B |

## Planning Modes

| Mode | Trigger | Steps |
|------|---------|-------|
| **Auto** | Default (or `--quick`) | Single-pass plan generation |
| **Interactive** | `--interactive` or auto (>= 10 sources / >= 20 blocks) | 1. Skeleton -> 2. Objectives -> 3. Design -> 4. Final plan |

## Agents (15)

### COLLECT (2)
| Agent | Role |
|-------|------|
| `source-scanner` | Scan files, detect types, extract metadata |
| `import-assessor` | Evaluate import complexity, recommend method |

### ASSESS (5)
| Agent | Role | Pathway |
|-------|------|---------|
| `audience-analyst` | Profile target audience | All |
| `content-strategist` | Analyze themes, coverage, gaps | All |
| `gap-analyst` | Compare current vs target state | A, B |
| `format-explorer` | Propose document formats | C |
| `angle-generator` | Propose narrative angles | C |

### PLAN (3)
| Agent | Role |
|-------|------|
| `structure-architect` | Design document skeleton and block mapping |
| `domain-researcher` | Research external best practices and references |
| `learnings-researcher` | Search docs/solutions/ for past patterns |

### REVIEW (5 perspectives)
| Perspective | Agent | Evaluates |
|-------------|-------|-----------|
| Reader/Learner | `audience-advocate` | Clarity, progression, engagement |
| Pedagogical | `pedagogy-analyst` | Objectives, alignment, rhythm |
| Visual | `visual-reviewer` | Coherence, readability, accessibility |
| Technical | `style-consistency-checker` | CSS, conventions, book.py |
| Editorial | `content-editor` | Writing quality, tone, terminology |

## Severity Levels (Review)

| Level | Meaning |
|-------|---------|
| **CRITICAL** | Blocks work or comprehension |
| **MAJOR** | Significantly degrades quality |
| **MINOR** | Minor polish needed |
| **SUGGESTION** | Nice to have improvement |

## Project Directory Structure

```
my-project/
  docs/
    collect/        # Source inventory reports
    assess/         # Requirements and objectives
    plans/          # Production plans
    reviews/        # Review reports
    solutions/      # Capitalized learnings
      structure/    # Document structure patterns
      style/        # CSS/theme patterns
      content/      # Content writing patterns
      process/      # Workflow patterns
      pedagogy/     # Pedagogical patterns
      assets/       # Asset management patterns
      deployment/   # Deploy/export patterns
      import/       # Import conversion patterns
```

## File Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Collect | `YYYY-MM-DD-<name>-collect.md` | `2026-03-22-info101-collect.md` |
| Assess | `YYYY-MM-DD-<name>-assess-<pathway>.md` | `2026-03-22-info101-assess-import.md` |
| Plan | `YYYY-MM-DD-NNN-<pathway>-<name>-plan.md` | `2026-03-22-001-import-info101-plan.md` |
| Review | `YYYY-MM-DD-<name>-review.md` | `2026-03-22-info101-review.md` |
| Solution | `YYYY-MM-DD-<topic>.md` | `2026-03-22-grid-layout-pattern.md` |

## Orchestrated StreamTeX Commands

### During PRODUCE
| Action | Commands used |
|--------|-------------|
| Import | `/stx-import:html`, `:html-block`, `:html-batch`, `:marp` |
| Create | `/stx-designer:init`, `:block-new`, `:slide-new` |
| Improve | `/stx-designer:update`, `:style-refactor` |
| Verify | `/stx-designer:audit --target`, `:fix --target` |
| Deliver | `/stx-export:html`, `/stx-deploy:deploy` |

### During REVIEW
| Action | Commands used |
|--------|-------------|
| Audit | `/stx-designer:audit --all` |
| Fix | `/stx-designer:fix` (with `--fix` flag) |
