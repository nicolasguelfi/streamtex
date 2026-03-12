Add a comment to an existing GitHub issue.

Arguments: $ARGUMENTS (format: `<id> <text>` or `--help`)

## Argument Parsing

Parse `$ARGUMENTS`:
- First token = **id** (integer, the issue number)
- Remaining tokens = **text** (free text for the comment)
- `--help` → show the help section below and stop

If id is missing or not an integer, ask the user to provide the issue number.
If text is missing, ask the user to provide the comment text.

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

Determine the target repo:

1. Check if inside a git repo with a GitHub remote:
   ```bash
   git remote get-url origin 2>/dev/null
   ```

2. If the remote is a StreamTeX ecosystem repo, use it directly.

3. If NOT in a StreamTeX repo, ask the user which repo to target.

4. Extract the owner/repo from the remote URL. If no remote, ask the user.

### Step 3 — Verify issue exists

```bash
gh issue view <id> --repo <owner>/<repo> --json title,state,number -q '.number, .title, .state'
```

If the issue does not exist, stop and show an error message.

### Step 4 — Display issue info

Show:
- Issue number and title
- Current state (open/closed)

### Step 5 — Preview comment

Display the comment text to the user for review.

Ask: **"Add this comment to issue #<id>? (yes/no)"**

Do NOT create the comment without explicit user confirmation.

### Step 6 — Create comment

```bash
gh issue comment <id> --repo <owner>/<repo> --body "<text>"
```

### Step 7 — Report

Display:
- Confirmation that the comment was added
- The issue URL

## Constraints

- NEVER create a comment without user confirmation (Step 5)
- ALWAYS preview the comment before creating
- NEVER include sensitive data (API keys, tokens, passwords) in the comment body

## Help

When `$ARGUMENTS` is `--help`, display:

```
/stx-issue:comment — Add a comment to an existing GitHub issue

Usage:
  /stx-issue:comment <id> <text>

Arguments:
  <id>     Issue number (integer)
  <text>   Comment text (free text)

Examples:
  /stx-issue:comment 42 Fixed in v0.3.1, please verify
  /stx-issue:comment 15 This also affects st_grid when using nested layouts
  /stx-issue:comment 7 Closing: resolved by PR #23

The comment is added to the issue in the detected repository.
You are always asked to confirm before submission.

Requires: gh CLI installed and authenticated (gh auth login)
```
