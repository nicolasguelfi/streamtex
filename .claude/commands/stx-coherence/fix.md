# /stx-coherence:fix — Fix coherence issues step by step

Arguments: $ARGUMENTS (optional: path to a plan file, or "auto" to run audit first — default: auto)

## Overview

This command fixes coherence issues **one at a time**, asking for user confirmation before each fix.
It follows a strict protocol: explain → propose → confirm → execute → verify.

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `auto` (default) — Run `/stx-coherence:audit` first to discover issues, then fix them
- `--errors-only` — Fix only ERRORs, skip WARNINGs
- `--warnings-only` — Fix only WARNINGs, skip ERRORs
- `--dry-run` — Show the plan without executing any fix
- `--help` — Show usage

### Examples

```
/stx-coherence:fix
/stx-coherence:fix --errors-only
/stx-coherence:fix --dry-run
```

## Workflow

### Phase 1: Discovery

1. **Run implicit audit**: Execute the `/stx-coherence:audit all` logic silently (do NOT display the full audit report).
2. **Collect all findings**: Gather all ERRORs and WARNINGs with their metadata:
   - Severity (ERROR / WARNING)
   - Check category (which of the 22 checks)
   - File path and line number
   - Description of the issue
   - Source of truth (if applicable)

### Phase 2: Plan Generation

1. **Sort findings** into an optimal execution order:
   - **Priority 1**: File sync errors (Check 4) — copy from source of truth, no risk
   - **Priority 2**: Source-of-truth fixes — fix the source first, then propagate
   - **Priority 3**: Code fixes in documentation blocks (Checks 13-15) — parameter names, enum values
   - **Priority 4**: Badge/counter fixes (Check 8) — requires counting first
   - **Priority 5**: Structural improvements (Checks 6-7) — templates, block structure
   - **Priority 6**: Exception list updates — adding known exceptions to coherence-checks.md
   - **Priority 7**: WARNINGs that require a decision (multiple options)

2. **Dependency ordering**: If fix B depends on fix A (e.g., fix the source before syncing copies), ensure A comes before B.

3. **Group related fixes**: If two fixes touch the same file, present them together but still confirm each one.

4. **Present the plan summary**:

```
## Coherence Fix Plan

Found: N errors, M warnings

### Execution order:
  1. [E1] SYNC coding_standards.md — copy from source of truth
  2. [E2] SYNC streamtex_cheatsheet_en.md — copy from source of truth
  3. [E3] FIX stx-guide.md:1124 — list_style= → l_style= (invalid param)
  ...

Files to modify: X
Estimated changes: Y

Ready to start? (y/n)
```

**Wait for user confirmation before proceeding to Phase 3.**

### Phase 3: Step-by-Step Execution

For EACH fix in the plan, follow this exact protocol:

#### Step 3a: Explain the problem

Present the issue with full context:

```
─────────────────────────────────────────────
Fix 1/N — [E1] File Sync: coding_standards.md
─────────────────────────────────────────────

**Problem**: The copy in `streamtex-docs/references/coding_standards.md` (794 lines)
is out of sync with the source of truth `streamtex-claude/shared/references/coding_standards.md`
(815 lines).

**Missing content**: Claude Code Integration section, User Customization section,
updated MarkerConfig defaults.

**Check**: #4 (Profile File Sync)
```

#### Step 3b: Propose the fix

Show exactly what will change:

```
**Proposed fix**:
  Action: Copy source → destination (full file replacement)
  Source: streamtex-claude/shared/references/coding_standards.md
  Target: streamtex-docs/references/coding_standards.md

  # For code edits, show the diff:
  # File: streamtex-claude/shared/commands/stx-guide.md
  # Line 1124:
  #   - with st_list(list_style=arrows) as l:
  #   + with st_list(l_style=arrows) as l:
```

#### Step 3c: Ask for confirmation

```
Apply this fix? (y = apply / n = skip / e = edit proposal / q = quit)
```

**Behavior**:
- **y** → Apply the fix, verify it worked, show result, move to next
- **n** → Skip this fix, move to next
- **e** → Ask the user what they want to change about the proposal, adjust, re-present
- **q** → Stop the fix session, show summary of what was done so far

#### Step 3d: Execute and verify

After applying:
1. Execute the fix (file copy, edit, or command)
2. **Verify** the fix was applied correctly (re-read the file, check line count, etc.)
3. Show a brief confirmation:

```
✓ Fix applied — coding_standards.md synced (815 lines)
```

4. If the fix requires propagation (e.g., `stx claude update --all`), note it:

```
⚠ Propagation needed: run `stx claude update --all` after all fixes
   (will be done at the end)
```

#### Step 3e: Move to next

Proceed to the next fix in the plan. Repeat 3a→3d.

### Phase 4: Post-fix Actions

After all individual fixes are done:

1. **Run propagation** if any source-of-truth files were modified:
   ```
   Propagating changes via `stx claude update --all`...
   ✓ Updated N files across M projects
   ```

2. **Run verification audit**:
   ```
   Running verification audit...
   ```
   Execute a quick `/stx-coherence:audit` to confirm the fixes resolved the issues.

3. **Show final summary**:

```
## Fix Session Summary

Applied: X/Y fixes
Skipped: Z fixes
Remaining issues: W

### Applied fixes:
  ✓ [E1] coding_standards.md synced
  ✓ [E2] cheatsheet synced
  ✓ [E3] stx-guide.md: list_style → l_style
  ⊘ [W3] stx-migration dirs — skipped by user

### Remaining issues (if any):
  - [W9] test_block_helpers.py — deferred (needs separate implementation)
```

## Fix Categories and Actions

### File sync fixes (Check 4)
- **Action**: `cp <source> <destination>`
- **Verify**: Compare line counts after copy

### Parameter/signature fixes (Checks 11, 14)
- **Action**: Edit specific lines in the file
- **Verify**: Grep the file to confirm old pattern is gone

### Badge/counter fixes (Check 8)
- **Action**: Edit the specific line with the badge value
- **Verify**: Read the line after edit

### Exception list updates (any check)
- **Action**: Add entries to the "Known exceptions" section of coherence-checks.md
- **Verify**: Read the updated section

### Orphan file cleanup (custom)
- **Action**: Remove orphan files/directories
- **Verify**: Confirm path no longer exists

### Decisions required (multiple options)
- **Action**: Present options A/B/C, ask user to choose, then execute
- **Verify**: Depends on chosen option

## Constraints

- **NEVER** apply a fix without user confirmation
- **NEVER** batch multiple fixes into one confirmation (one fix = one confirmation)
- **NEVER** modify the `streamtex` library code without explicit user approval
- Always show the exact file path and line numbers
- Always show before/after for code edits
- If a fix could affect other files (propagation), mention it explicitly
- If unsure about a fix, present it as a decision with options rather than a direct fix
- Keep explanations concise but complete — the user needs enough context to make an informed decision
