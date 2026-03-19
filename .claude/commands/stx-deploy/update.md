# /stx-deploy:update — Update deployed projects

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[OPTIONS]`

**Options**:
- `--project NAME` — Update a specific project
- `--all` — Update all deployed projects
- `--force` — Force rebuild even if no changes detected

### Examples

```
/stx-deploy:update --project cours-python
/stx-deploy:update --all
/stx-deploy:update --all --force
```

## Required readings BEFORE execution

1. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Load state

Read `.stx-deploy.json` to get the list of deployed projects.

If no projects deployed:
```
No projects deployed yet. Deploy with: /stx-deploy:deploy [path]
```

### Step 3: Select projects to update

If `--project NAME`: find the matching project in `.stx-deploy.json`.
If `--all`: select all projects.
If neither: ask the user which project(s) to update.

### Step 4: Trigger redeploy

For each selected project, trigger a redeploy via Coolify:

**Option A — Via Coolify API** (if API token available):
```bash
curl -X POST "https://coolify.$DOMAIN/api/v1/applications/$APP_UUID/restart" \
  -H "Authorization: Bearer $COOLIFY_TOKEN"
```

**Option B — Via Coolify UI** (guide the user):
```
In Coolify dashboard:
1. Projects → $PROJECT_NAME → Deploy
```

**Option C — Via git push** (if auto-deploy is enabled):
```
The project has auto-deploy enabled.
Push a change to trigger a rebuild:
  cd $PROJECT_PATH
  git commit --allow-empty -m "Trigger rebuild"
  git push origin main
```

### Step 5: Monitor deployment

For each project being updated:
1. Wait for build to start
2. Monitor health check endpoint
3. Report when the new version is live

```bash
# Poll health check
curl -s "https://$SUBDOMAIN/_stcore/health"
```

### Step 6: Display result

```
Update Complete:
  #  Project          Status    Duration
  1  cours-python     updated   45s
  2  cours-docker     updated   38s

All health checks passing.
```
