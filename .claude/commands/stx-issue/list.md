List GitHub issues for a repository.

Arguments: $ARGUMENTS (format: `[--repo <owner/repo>] [--state <open|closed|all>]` or `--help`)

## Argument Parsing

Parse `$ARGUMENTS`:
- `--repo <owner/repo>` — target repository (optional, auto-detected if omitted)
- `--state <open|closed|all>` — issue state filter (optional, default: `open`)
- `--help` → show the help section below and stop

## Workflow

### Step 1 — Prerequisites check

Run these commands (read-only, execute directly):

```bash
gh auth status
```

If `gh` is not installed or not authenticated, stop and show:
- Install: `brew install gh` (macOS) or see https://cli.github.com
- Auth: `gh auth login`

### Step 2 — Detect target repository

If `--repo` was provided, use it directly.

Otherwise, determine the target repo:

1. Check if inside a git repo with a GitHub remote:
   ```bash
   git remote get-url origin 2>/dev/null
   ```

2. If the remote is a StreamTeX ecosystem repo, use it directly.

3. If NOT in a StreamTeX repo, ask the user which repo to target.

4. Extract the owner/repo from the remote URL. If no remote, ask the user.

### Step 3 — List issues

```bash
gh issue list --repo <owner>/<repo> --state <state> --limit 20
```

### Step 4 — Display formatted table

Display the results in a clean formatted table showing:
- Issue number (#)
- State (open/closed)
- Title
- Labels
- Date created

If no issues found, display a message indicating no issues match the filter.

## Constraints

- This is a read-only command — no confirmation needed
- NEVER modify any issues (this command only lists)

## Help

When `$ARGUMENTS` is `--help`, display:

```
/stx-issue:list — List GitHub issues for a repository

Usage:
  /stx-issue:list [--repo <owner/repo>] [--state <open|closed|all>]

Options:
  --repo <owner/repo>     Target repository (auto-detected if omitted)
  --state <state>         Filter by state: open (default), closed, all

Examples:
  /stx-issue:list                                    # Open issues in current repo
  /stx-issue:list --state all                         # All issues in current repo
  /stx-issue:list --repo nicolasguelfi/streamtex      # Open issues in streamtex
  /stx-issue:list --repo nicolasguelfi/streamtex-docs --state closed

Requires: gh CLI installed and authenticated (gh auth login)
```
