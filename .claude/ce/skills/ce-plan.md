# CE Plan

Skill for the PLAN phase of the Compound Engineering cycle. Create a structured production plan from the assessment. Supports two modes: auto (default) and interactive.

## Workflow

### Phase 0: Load Assessment

1. Scan `docs/assess/` for the most recent assessment file.
2. If no assessment is found, inform the user and suggest running `/stx-ce:assess` first. Do not proceed.
3. Parse the assessment to extract pathway, requirements, audience profile, and gap analysis.

### Phase 1: Research

1. Use the **learnings-researcher** agent to search `docs/solutions/` for relevant patterns and lessons learned from previous projects.
2. Use the **content-strategist** agent to validate that the planned content covers all requirements from the assessment.
3. If `--deep` flag is set: run all available agents in parallel for comprehensive research before planning. This includes domain-researcher, format-explorer, and angle-generator in addition to the above.

### Phase 2: Plan

#### Auto Mode (default)

1. The **structure-architect** agent generates the full plan in one pass based on:
   - Assessment requirements
   - Research findings
   - Pathway constraints
2. The plan includes: document skeleton, per-section objectives, design choices, and production sequence.

#### Interactive Mode (--interactive flag)

Execute 4 steps with user dialogue between each.

**Step 1 - Skeleton:**
1. The **structure-architect** agent proposes a document structure (parts, sections, blocks).
2. Present the skeleton to the user for validation.
3. User can modify, reorder, add, or remove sections.

**Step 2 - Objectives:**
1. The **content-strategist** agent proposes per-section objectives and content outlines.
2. The **audience-analyst** agent validates that objectives match the target audience.
3. Present to the user for adjustments.

**Step 3 - Design:**
1. The **visual-reviewer** agent (in conseil mode) proposes visual options:
   - Color scheme
   - Layout patterns
   - Typography choices
   - Asset strategy (images, diagrams, icons)
2. Present options to the user for selection.

**Step 4 - Final Plan:**
1. The **structure-architect** agent assembles the complete plan from validated choices.
2. The **learnings-researcher** agent enriches with applicable patterns from previous solutions.

### Phase 3: Generate Plan Document

1. Determine the daily sequence number by scanning `docs/plans/` for files matching today's date (`YYYY-MM-DD-NNN-*`). Increment NNN from the highest found, or start at 001.
2. Write to `docs/plans/YYYY-MM-DD-NNN-<pathway>-<name>-plan.md` using the pathway-specific template from `.claude/ce/templates/`.
3. The plan document must include:
   - Document structure with all sections and blocks
   - Per-section: objective, content outline, block type, estimated effort
   - Design specifications (colors, styles, layout)
   - Production sequence (order of execution)
   - Asset list (images, diagrams, code samples needed)
   - Deployment configuration (if applicable)
   - Total effort estimate
4. **GATE**: Present the plan summary to the user and ask for explicit validation before proceeding. The plan must be approved to continue.
5. Suggest next step: run `/stx-ce:produce` to execute the plan.
