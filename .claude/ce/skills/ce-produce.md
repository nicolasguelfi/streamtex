# CE Produce

Skill for the PRODUCE phase of the Compound Engineering cycle. Execute the production plan item by item, creating, importing, or improving content as specified.

## Workflow

### Phase 1: Initialize

1. Load the approved plan from `docs/plans/`. Use the most recent plan file unless a specific path is provided.
2. If the target project does not exist yet, run `/stx-designer:init --template <type>` where type is derived from the plan (project, presentation, collection, course).
3. Create a task list from the plan items. Each task has:
   - ID (sequential)
   - Description
   - Type (IMPORT, IMPROVE, CREATE)
   - Target block name
   - Status (pending, in-progress, done, failed)
4. Configure `book.py` according to the plan:
   - Set document metadata (title, author, description)
   - Configure navigation style
   - Set theme and style parameters

### Phase 2: Produce Iteratively

Process each plan item according to its type. After each item, mark it complete in the task list.

#### IMPORT Items

1. Run the appropriate import command based on source format:
   - HTML sources: `/stx-import:html`
   - Marp sources: `/stx-import:marp`
   - Other formats: manual conversion following plan instructions
2. Run `/stx-designer:audit --target <block>` on the imported block.
3. Run `/stx-designer:fix --target <block>` to resolve any issues found.
4. Verify the block renders correctly.

#### IMPROVE Items

1. Run `/stx-designer:update` with the improvement instructions from the plan.
2. If style changes are needed, run `/stx-designer:style-refactor`.
3. Run `/stx-designer:audit --target <block>` on the modified block.
4. Run `/stx-designer:fix --target <block>` to resolve any issues found.
5. Verify the block renders correctly.

#### CREATE Items

1. Create the block using `/stx-designer:block-new` or `/stx-designer:slide-new` as appropriate.
2. Write content according to the plan's content outline for this section.
3. Apply styles as specified in the plan's design section.
4. Integrate assets (images, diagrams, code samples) as listed in the plan.
5. Run `/stx-designer:audit --target <block>` on the new block.
6. Run `/stx-designer:fix --target <block>` to resolve any issues found.
7. Verify the block renders correctly.

### Phase 3: Global Verification

1. Run `/stx-designer:audit --all` to check the entire project.
2. Verify `book.py` navigation:
   - All blocks are registered in the correct order.
   - No blocks are missing from the plan.
   - Navigation flow is correct (previous/next links).
3. Perform a preview check to ensure the document renders as expected.
4. If audit reveals critical issues, fix them before proceeding.

### Phase 4: Deliver

1. If the plan requires HTML export, run `/stx-export:html`.
2. If the plan requires deployment (and `--no-deploy` is not set), run `/stx-deploy:deploy`.
3. Mark the plan as DONE in `docs/plans/` by updating the plan file status field.
4. Produce a production summary listing:
   - Items completed (with status)
   - Items that required manual intervention
   - Audit results
   - Deployment status (if applicable)
5. Suggest next step: run `/stx-ce:review` for a multi-perspective quality review.
