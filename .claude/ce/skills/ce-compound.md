# CE Compound

Skill for the COMPOUND phase of the Compound Engineering cycle. Capitalize learnings from the completed cycle to improve future iterations.

## Workflow

### Phase 0: Scan Context

1. Review auto-memory for any notes from the current project cycle.
2. Scan recent project history: review report, plan, assessment, and collect report.
3. Build a timeline of what happened during this cycle.

### Phase 1: Extract Learnings

Run 5 analysis perspectives sequentially to extract knowledge from the cycle.

1. **Context Analyzer**:
   - What was the document type (course, presentation, report, manual)?
   - Who was the target audience?
   - What was the primary objective?
   - Which pathway was used (A/B/C/mixed)?

2. **Solution Extractor**:
   - What patterns or techniques worked particularly well?
   - Which StreamTeX features were key to success?
   - What reusable code snippets or block patterns emerged?
   - What content structures proved effective?

3. **Related Finder**:
   - What other documents in the workspace are related to this one?
   - What cross-references or shared patterns exist?
   - Could any learnings apply to those related projects?

4. **Prevention Strategist**:
   - What problems were encountered during the cycle?
   - What went wrong and how was it resolved?
   - What should be avoided next time?
   - What warnings or precautions should be documented?

5. **Category Classifier**:
   - Assign each learning to one or more categories:
     - `structure`: document organization, navigation, skeleton patterns
     - `style`: visual design, CSS, theming, layout
     - `content`: writing, pedagogy, examples, exercises
     - `process`: workflow, tooling, automation, efficiency
     - `pedagogy`: learning design, assessment, progression
     - `assets`: images, diagrams, code samples, media
     - `deployment`: hosting, CI/CD, export, delivery
     - `import`: conversion, migration, format handling

### Phase 2: Check for Duplicates

1. Use the **learnings-researcher** agent to search `docs/solutions/` for similar existing entries.
2. For each candidate learning:
   - If a duplicate is found: update the existing solution file with new insights rather than creating a new one.
   - If a partial match is found: extend the existing solution with the new perspective.
   - If no match: prepare for creation as a new entry.

### Phase 3: Assemble and Write

1. For each new or updated learning:
   - Write to `docs/solutions/<category>/YYYY-MM-DD-<topic>.md` using the **solution** template from `.claude/ce/templates/`.
   - Include:
     - Context (when this applies)
     - Problem or opportunity
     - Solution or pattern
     - StreamTeX code examples where applicable
     - Related learnings (cross-references)
     - Tags for searchability
2. Create the category subdirectory if it does not exist.

### Phase 4: Summary

1. Report what was capitalized:
   - Number of new learnings created
   - Number of existing learnings updated
   - Categories covered
   - File paths of all written solutions
2. Suggest next cycle:
   - Run `/stx-ce:collect` to start a new cycle with new material.
   - Run `/stx-ce:assess` to reassess and improve the current project.
