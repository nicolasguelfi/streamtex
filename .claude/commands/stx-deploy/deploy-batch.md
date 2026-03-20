# /stx-deploy:deploy-batch — Deploy multiple StreamTeX projects

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[PATH] [OPTIONS]`

- **PATH**: Path to a directory containing multiple projects (default: `projects/`)

**Options**:
- `--domain DOMAIN` — Base domain for subdomain generation (default: from `.stx-deploy.json`)
- `--memory LIMIT` — Memory limit per project (default: `1g`)
- `--pattern GLOB` — Filter subdirectories (default: `*`)
- `--dry-run` — Show what would be deployed without executing

### Examples

```
/stx-deploy:deploy-batch
/stx-deploy:deploy-batch ./projects --domain mysite.com
/stx-deploy:deploy-batch ./projects --pattern "cours-*" --dry-run
/stx-deploy:deploy-batch ./streamtex-docs/manuals --pattern "stx_manual_*"
```

## Required readings BEFORE execution

1. `.claude/developer/skills/hetzner-infrastructure.md` — infrastructure reference
2. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Load state and verify infrastructure

Read `.stx-deploy.json` and verify phases 1-4 are completed.

### Step 3: Discover projects

Scan PATH for StreamTeX projects:
```bash
# Find directories containing book.py
find $PATH -maxdepth 2 -name "book.py" -exec dirname {} \;
```

Apply `--pattern` filter if specified.

### Step 4: Generate deployment plan

For each discovered project, determine:
- Project name (from directory name)
- Subdomain: `{name}.{domain}`
- Estimated memory profile (check imports in book.py for pandas/plotly/AI → Doc/Data/AI)
- Whether it's already deployed (check `.stx-deploy.json`)

Display the plan:
```
Deployment Plan:
  Domain: mondomaine.com
  Projects found: N

  #  Project          Subdomain                      Profile  Memory  Status
  1  cours-python     cours-python.mondomaine.com     Doc      1g     NEW
  2  cours-docker     cours-docker.mondomaine.com     Doc      1g     NEW
  3  dashboard-ml     dashboard-ml.mondomaine.com     Data     2g     NEW
  4  cours-intro      cours-intro.mondomaine.com      Doc      1g     DEPLOYED (skip)

  Total new: 3 projects
  Estimated RAM: 3.3 GB (idle) + overhead = 4.5 GB
  Server capacity: 14.8 GB available → OK

Proceed? (yes/no)
```

### Step 5: Handle dry-run

If `--dry-run`: display the plan and stop. Do not deploy.

### Step 6: Deploy each project

For each NEW project (skip already deployed):
1. Run `/stx-deploy:deploy $PROJECT_PATH --domain $SUBDOMAIN --memory $MEMORY`
2. Wait for health check
3. Report progress: `[2/3] cours-docker deployed ✓`

If a deployment fails:
- Report the error
- Ask the user: continue with remaining projects or stop?
- Record the failure in the plan

### Step 7: Check CDN status

Read `.stx-deploy.json` and check if `cdn.enabled` is true.

If CDN is NOT configured, append a reminder:
```
Tip: Your server has no CDN or bot protection yet.
     Run /stx-deploy:configure-domain to set up Cloudflare (free).
```

### Step 8: Display summary

```
Batch Deployment Complete:
  Deployed: 3/3
  Failed: 0
  CDN:     $CDN_STATUS

  #  Project          URL                              Status
  1  cours-python     https://cours-python.mondomaine.com   running
  2  cours-docker     https://cours-docker.mondomaine.com   running
  3  dashboard-ml     https://dashboard-ml.mondomaine.com   running

Check all: /stx-deploy:status --all
```
