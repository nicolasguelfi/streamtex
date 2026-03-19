# /stx-deploy:preflight — Verify deployment prerequisites

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[PATH]`

- **PATH**: Path to the StreamTeX project to check (default: current directory)

### Examples

```
/stx-deploy:preflight
/stx-deploy:preflight ./projects/cours-python
```

## Required readings BEFORE execution

1. `.claude/developer/skills/hetzner-infrastructure.md` — infrastructure reference
2. `.claude/developer/agents/deploy-operator.md` — deployment agent role

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt the role defined in `.claude/developer/agents/deploy-operator.md`.

### Step 2: Check local project structure

Run these checks on the project at PATH:

| # | Check | How | Required |
|---|-------|-----|----------|
| 1 | `book.py` exists | Glob for `book.py` at project root | Yes |
| 2 | `pyproject.toml` has streamtex dep | Read `pyproject.toml`, search for `streamtex` in dependencies | Yes |
| 3 | `.streamlit/config.toml` exists | Glob for `.streamlit/config.toml` | Yes |
| 4 | CORS disabled | Read config.toml, verify `enableCORS = false` | Yes |
| 5 | XSRF disabled | Read config.toml, verify `enableXsrfProtection = false` | Yes |
| 6 | Headless mode | Read config.toml, verify `headless = true` | Yes |
| 7 | Dockerfile present | Glob for `Dockerfile` | Warn if absent (can be generated) |
| 8 | No sensitive files | Glob for `.env`, `credentials*`, `*.key`, `*.pem` | Warn if found |
| 9 | Git clean | `git status --porcelain` | Warn if dirty |
| 10 | Tests pass | `uv run pytest tests/ -v` (if tests/ exists) | Warn if fail |

### Step 3: Check local tools

| # | Check | How | Required |
|---|-------|-----|----------|
| 11 | Docker installed | `docker --version` | Yes |
| 12 | SSH key exists | Glob `~/.ssh/id_ed25519.pub` or `~/.ssh/id_rsa.pub` | Yes |
| 13 | hcloud CLI | `hcloud version` | Recommended (show install instructions if absent) |
| 14 | Credentials file | Check `~/.stx-deploy.env` exists and contains `HETZNER_API_TOKEN` | Recommended |

### Step 4: Check existing deployment state

If `.stx-deploy.json` exists in the workspace root:
- Read it and display current infrastructure state
- Show which phases are already completed
- Indicate next recommended phase

### Step 5: Display results

Output a table with columns: `#`, `Check`, `Status` (PASS/WARN/FAIL), `Details`.

Count totals: N passed, N warnings, N failures.

If all required checks pass:
```
Ready for deployment. Next step: /stx-deploy:provision
```

If any required check fails:
```
Fix the FAIL items above before proceeding.
```

### Step 6: Fix suggestions

For each FAIL or WARN, provide a one-line fix suggestion:
- Missing `config.toml` → `mkdir -p .streamlit && cat > .streamlit/config.toml ...`
- Missing Dockerfile → `stx deploy docker . --build-only`
- Missing SSH key → `ssh-keygen -t ed25519`
- Missing hcloud → `brew install hcloud` or `pip install hcloud`
- Missing credentials → `echo "HETZNER_API_TOKEN=your-token" >> ~/.stx-deploy.env`
