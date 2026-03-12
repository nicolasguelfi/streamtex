Create a GitHub **feature request** with auto-collected environment metadata.

Arguments: $ARGUMENTS (format: `<description>` or `--help`)

## Argument Parsing

Parse `$ARGUMENTS`:
- All tokens = **description** (free text describing the feature)
- `--help` → show the help section below and stop

If description is missing, ask the user to describe the feature.

## Issue Type

| Type | GitHub Label | Title Prefix (fallback) |
|------|-------------|------------------------|
| `feature` | `enhancement` | `[Feature]` |

## Workflow

### Step 1 — Prerequisites check

Run these commands (read-only, execute directly):

```bash
gh auth status
```

If `gh` is not installed or not authenticated, stop and show:
- Install: `brew install gh` (macOS) or see https://cli.github.com
- Auth: `gh auth login`

### Step 2 — Collect environment metadata

Run these commands silently and collect results:

```bash
# StreamTeX version
uv pip show streamtex 2>/dev/null | grep Version | awk '{print $2}'

# Python version
python3 --version 2>/dev/null | awk '{print $2}'

# OS
uname -srm

# uv version
uv --version 2>/dev/null | awk '{print $2}'

# Project name (from pyproject.toml if exists)
grep '^name' pyproject.toml 2>/dev/null | head -1 | sed 's/.*= *"\(.*\)"/\1/'

# Workspace preset (from stx.toml if exists)
grep 'preset' ../../stx.toml 2>/dev/null | sed 's/.*= *"\(.*\)"/\1/'

# Profile (from .claude/.stx-profile if exists)
cat .claude/.stx-profile 2>/dev/null

# Git branch
git branch --show-current 2>/dev/null

# Last commit
git rev-parse --short HEAD 2>/dev/null
```

### Step 3 — Detect target repository

Determine the most appropriate repo based on context:

1. Check if inside a git repo with a GitHub remote:
   ```bash
   git remote get-url origin 2>/dev/null
   ```

2. If the remote is a StreamTeX ecosystem repo, use it directly.

3. If NOT in a StreamTeX repo (user project), route intelligently:
   - Feature for library API, new `st_*` functions → `streamtex`
   - Feature for documentation, manuals → `streamtex-docs`
   - Feature for Claude profiles, commands → `streamtex-claude`
   - If ambiguous, ask the user.

4. Extract the owner/repo from the remote URL. If no remote, ask the user which repo to target.

### Step 4 — Check permissions on target repo

```bash
gh repo view <owner>/<repo> --json viewerPermission -q '.viewerPermission'
```

- `WRITE` or `ADMIN` → labels will be applied
- `READ` → skip labels, use title prefix `[Feature]`
- No access → stop with error message

### Step 5 — Gather additional details

Ask the user:
1. Motivation / use case
2. Proposed solution (optional)

### Step 6 — Choose language

Ask the user: "English or French? (English is recommended for GitHub issues)"

Default to English if the user does not express a preference.

### Step 7 — Compose the issue

Build the issue title and body:

**Title**: concise summary from the description (max 80 chars)

**Body template**:

```markdown
## Description
<user's description>

## Motivation
...

## Proposed Solution
...

## Environment
| Key | Value |
|-----|-------|
| StreamTeX | <version> |
| Python | <version> |
| OS | <os> |
| UV | <version> |
| Project | <name or N/A> |
| Preset | <preset or N/A> |
| Profile | <profile or N/A> |
| Branch | <branch> |
| Commit | <short hash> |
```

### Step 8 — Preview and confirm

Display the full issue (title + body) to the user in a formatted preview.

Ask: **"Create this issue? (yes/no)"**

Do NOT create the issue without explicit user confirmation.

### Step 9 — Create the issue

Based on permissions detected in Step 4:

**With write access:**
```bash
gh issue create --repo <owner>/<repo> --title "<title>" --body "<body>" --label "enhancement"
```

**Without write access (read-only):**
```bash
gh issue create --repo <owner>/<repo> --title "[Feature] <title>" --body "<body>"
```

### Step 10 — Report

Display:
- The issue URL (returned by `gh issue create`)
- The repo it was created in
- The labels applied (if any)

## Constraints

- NEVER create an issue without user confirmation (Step 8)
- ALWAYS preview the full issue before creating
- NEVER include sensitive data (API keys, tokens, passwords) in the issue body
- If `pyproject.toml` contains `.env` references or secrets, strip them from metadata
- Default language is English; French only if user explicitly requests it

## Help

When `$ARGUMENTS` is `--help`, display:

```
/stx-issue:feature — Request a feature with auto-collected metadata

Usage:
  /stx-issue:feature <description>

Examples:
  /stx-issue:feature Add dark mode toggle to st_book sidebar
  /stx-issue:feature Support for custom color palettes in st_grid
  /stx-issue:feature Export to PPTX format

Metadata collected automatically:
  StreamTeX version, Python version, OS, uv version,
  project name, workspace preset, Claude profile,
  git branch, last commit hash

The issue is created on the appropriate StreamTeX repo
(streamtex, streamtex-docs, or streamtex-claude) based
on the context. You are always asked to confirm before creation.

Requires: gh CLI installed and authenticated (gh auth login)
```
