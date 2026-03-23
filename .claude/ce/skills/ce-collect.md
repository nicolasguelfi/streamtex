# CE Collect

Skill for the COLLECT phase of the Compound Engineering cycle. Inventory and classify existing material from various sources to prepare for assessment.

## Workflow

### Phase 0: Resume Check

1. Check if `docs/collect/` exists and contains a previous session file.
2. If a file matching `YYYY-MM-DD-*-collect.md` exists for today, ask the user whether to resume or start fresh.
3. If resuming, load the existing report and skip to the phase where it left off.

### Phase 1: Scan Sources

Use the **source-scanner** agent to inventory all available material.

1. Accept a path argument from the user, or prompt for the source location using AskUserQuestion.
2. Determine scan mode based on flags:
   - `--project`: scan the existing StreamTeX project structure (blocks/, book.py, assets/).
   - `--url`: fetch web content from the provided URL for analysis.
   - Default: scan the provided local path for files (HTML, Markdown, PDF, PPTX, Marp, images).
3. For each source found, record:
   - File path or URL
   - Format (html, md, marp, pptx, pdf, image, other)
   - Size and estimated content volume
   - Language (if detectable)
4. Produce a raw inventory list.

### Phase 2: Classify

Use the **content-strategist** agent to organize the inventory.

1. Group sources by theme or topic based on content analysis.
2. Detect duplicates or near-duplicates across sources.
3. Identify dependencies between sources (e.g., an image referenced by an HTML file).
4. Flag sources that are complementary vs. redundant.
5. Produce a classified inventory with theme groups.

### Phase 3: Evaluate Importability

Use the **import-assessor** agent to evaluate each source.

1. For each source, determine:
   - **Complexity**: simple (text-only), moderate (text + images), complex (interactive, animations, custom layouts)
   - **Import method**: automatic (/stx-import:html, /stx-import:marp), semi-automatic, manual conversion
   - **Target format**: which StreamTeX block type(s) would best represent this content
   - **Effort estimate**: low (< 5 min), medium (5-30 min), high (> 30 min)
2. Flag sources that cannot be imported and explain why.
3. Compute total effort estimate.

### Phase 4: Generate Report

1. Write the collect report to `docs/collect/YYYY-MM-DD-<name>-collect.md` using the **collect-report** template from `.claude/ce/templates/`.
2. The report must include:
   - Source inventory with classification
   - Importability assessment per source
   - Recommended pathway:
     - **A (Import)**: majority of content comes from external sources
     - **B (Improve)**: content already exists as a StreamTeX project
     - **C (Create)**: content must be created from scratch
     - **Mixed**: combination of pathways (specify which sources map to which pathway)
   - Total effort estimate
3. Suggest next step: run `/stx-ce:assess` to evaluate the collected material and define objectives.
