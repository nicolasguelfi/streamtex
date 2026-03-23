# CE Assess

Skill for the ASSESS phase of the Compound Engineering cycle. Evaluate existing material and define objectives through structured dialogue with the user.

## Workflow

### Phase 0: Auto-Detect Pathway

1. Check `docs/collect/` for reports containing external sources. If found, enable mode **IMPORT (A)**.
2. Check if the current directory is a StreamTeX project with a `blocks/` directory. If found, enable mode **IMPROVEMENT (B)**.
3. If neither condition is met, set mode to **CREATION (C)**.
4. If both conditions 1 and 2 are met, combine **A+B** (import and improve).
5. Log the detected pathway for the user.

### Phase 1: Evaluate

Evaluation strategy depends on the detected pathway.

#### Pathway A (Import)

1. Use the **audience-analyst** agent to profile the target audience from collected sources.
2. Use the **content-strategist** agent to evaluate content quality, coverage, and coherence.
3. Use the **gap-analyst** agent to identify gaps between collected material and a complete document.

#### Pathway B (Improvement)

1. Run `/stx-designer:audit --all` to get the current project quality report.
2. Use the **gap-analyst** agent to compare current state vs. target quality level.
3. Identify blocks that need rework, missing sections, and style inconsistencies.

#### Pathway C (Creation)

1. Use the **audience-analyst** agent to help define the target audience.
2. Use the **content-strategist** agent to explore content scope and structure.
3. Use the **domain-researcher** agent to gather domain knowledge and best practices.
4. Use the **format-explorer** agent to suggest document formats and presentation styles.
5. Use the **angle-generator** agent to propose original angles and approaches.

### Phase 2: Dialogue with User

Ask focused questions to capture requirements R1 through R18. Use AskUserQuestion for each group.

1. **Identity** (R1-R3):
   - R1: Document title
   - R2: Document type (course, presentation, report, manual, collection)
   - R3: Author / organization context
2. **Content** (R4-R8):
   - R4: Subject matter and scope
   - R5: Key topics to cover
   - R6: Target depth (introductory, intermediate, advanced)
   - R7: Prerequisites assumed
   - R8: Learning objectives or document goals
3. **Form** (R9-R12):
   - R9: Visual style preferences
   - R10: Branding constraints (colors, logos, fonts)
   - R11: Navigation style (linear, tabbed, sidebar)
   - R12: Estimated length (number of sections/slides)
4. **Delivery** (R13-R15):
   - R13: Target platform (web, PDF, both)
   - R14: Deployment target (local, Render, Hetzner, other)
   - R15: Timeline and deadlines
5. **Sources** (R16-R18, pathway A only):
   - R16: Priority ranking of collected sources
   - R17: Content to exclude or skip
   - R18: Adaptation instructions (update, simplify, restructure)

### Phase 3: Generate Assessment Document

1. Write to `docs/assess/YYYY-MM-DD-<name>-assess-<pathway>.md` using the appropriate pathway template from `.claude/ce/templates/`.
2. The document must include:
   - Detected pathway with justification
   - Audience profile
   - Requirements R1-R18 (as captured)
   - Content evaluation results
   - Gap analysis findings
   - Recommended approach for the PLAN phase
3. Suggest next step: run `/stx-ce:plan` to create a structured production plan.
