Assisted code migration for a StreamTeX project: $ARGUMENTS

This skill fixes compatibility issues detected by `stx project upgrade --check`.
It handles REMOVED, RENAMED, and PARAM_REMOVED issues, plus semantic migrations
that require human judgment.

## Step 1: Detect Issues

Run the compatibility checker on the project:

```
uv run stx project upgrade --check .
```

Parse the output. The checker produces a table with columns:
- **File** — relative path to the affected `.py` file
- **Line** — line number of the issue
- **Severity** — `error` or `warning`
- **Code** — one of: `REMOVED`, `RENAMED`, `PARAM_REMOVED`, `PARSE_ERROR`
- **Message** — human-readable description

Below the table, a **Suggestions** section lists recommended fixes per issue.

If the output says "No compatibility issues found", inform the user and skip to Step 5.

## Step 2: Plan Fixes

For each issue, determine the fix strategy:

### RENAMED issues
- Straightforward find-and-replace.
- Replace **all occurrences** of the old name with the new name in the affected file:
  imports, function calls, decorator usages, string references in `__all__`.
- Example: `st_grid_layout` -> `st_grid` means replacing every `st_grid_layout` token.

### REMOVED issues
- Read the suggestion text (e.g., "Use st_markdown(file=...) instead.").
- Open the affected file and read the surrounding context (10 lines before and after).
- Determine the replacement API call and rewrite the usage.
- If no suggestion is provided, search the streamtex cheatsheet
  (`.claude/references/streamtex_cheatsheet_en.md`) for the closest replacement API.
- If no obvious replacement exists, flag it to the user and ask for guidance.

### PARAM_REMOVED issues
- Open the affected file at the indicated line.
- Remove the deprecated keyword argument from the function call.
- Read the suggestion (e.g., "Use toc_config=None to disable TOC.") and apply the
  recommended alternative if one exists.
- If the removed parameter controlled important behavior, add a comment
  `# TODO(migrate): verify behavior after removing '<param>'` so the user reviews it.

### PARSE_ERROR issues
- The file has a syntax error. Report it to the user — do NOT attempt automated fixes.

## Step 3: Apply Fixes

For each affected file, apply all planned changes:

1. Read the full file content.
2. Apply the edits (renames, removals, rewrites).
3. Run `uv run ruff check <file> --fix` to fix import ordering and style.
4. Show the user a summary of what changed in that file.

Important rules:
- Never remove or rewrite code beyond what the compatibility issue requires.
- Preserve comments, docstrings, and formatting style of the original file.
- If a REMOVED API was used in multiple places within the same file, fix ALL occurrences.
- If an import is no longer needed after the fix, remove it.
- If a new import is needed, add it in the correct location (ruff will sort it).

## Step 4: Verify Fixes

After all fixes are applied:

1. Re-run the compatibility check:
   ```
   uv run stx project upgrade --check .
   ```
2. Confirm that all previously reported issues are resolved.
3. If new issues appear (unlikely but possible with cascading changes), go back to Step 2.
4. Run linting to ensure code quality:
   ```
   uv run ruff check . --fix
   ```

## Step 5: Apply Structural Migrations

Once compatibility issues are resolved, apply the remaining upgrade steps:

```
uv run stx project upgrade --skip-sync
```

This applies structural migrations (file additions, config updates, version marker bump)
without re-running `uv sync` (the user can do that separately if needed).

Review the output and report what migrations were applied.

## Step 6: Final Report

Present a summary to the user:

```
Migration Summary
=================
Project:  <project name>
From:     <old version>
To:       <new version>

Issues fixed:
  - <file>:<line> [RENAMED] old_name -> new_name
  - <file>:<line> [REMOVED] old_api -> replacement
  - <file>:<line> [PARAM_REMOVED] func(param=...) -> func(...)

Structural migrations applied:
  - v0.X.Y: <description>

Remaining manual actions:
  - <any items that need human review>
  - Run: uv sync
  - Run: stx project validate
```

## Edge Cases

- **No issues found but version is behind**: This means only structural migrations are
  needed. Skip to Step 5 directly.
- **User provides a specific file path as argument**: Only check and fix that file, but
  still run the full `--check` at the end to verify nothing else is broken.
- **Multiple projects in workspace**: If the user says "migrate all", iterate over each
  project directory under `projects/`. Otherwise, migrate only the current directory.
- **Semantic changes without a code pattern**: Some breaking changes alter behavior
  without changing the API signature (e.g., a default value change). The suggestion text
  will describe these. Add a `# TODO(migrate):` comment and inform the user.
