# /stx-deploy:deploy — Deploy a StreamTeX project to Hetzner

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `[PATH] [OPTIONS]`

- **PATH**: Path to the StreamTeX project (default: current directory)

**Options**:
- `--domain SUBDOMAIN` — Full subdomain (e.g. `cours-python.mondomaine.com`). Default: auto-generated from project directory name.
- `--memory LIMIT` — Container memory limit (default: `1g`)
- `--cpu LIMIT` — Container CPU limit (default: `1.0`)
- `--env KEY=VALUE` — Environment variable (repeatable)
- `--server NAME` — Target server if multi-server setup (default: primary)
- `--folder PATH` — For multi-manual deploys, the FOLDER env var
- `--help` — Show deployment guide

### Examples

```
/stx-deploy:deploy
/stx-deploy:deploy ./projects/cours-python --domain cours-python.mysite.com
/stx-deploy:deploy ./streamtex-docs --folder manuals/stx_manual_intro --domain docs-intro.mysite.com
/stx-deploy:deploy . --memory 2g --env STX_PASSWORD=secret
```

## Required readings BEFORE execution

1. `.claude/developer/skills/hetzner-infrastructure.md` — Streamlit config requirements
2. `.claude/developer/agents/deploy-operator.md` — deployment protocol

## Workflow

### Step 1: Adopt the Deploy Operator role

Read and adopt `.claude/developer/agents/deploy-operator.md`.

### Step 2: Load state

Read `.stx-deploy.json`:
- Verify phases 1-4 are completed (provision, secure, install-coolify, configure-domain)
- Get domain, server info, Coolify URL
- Check if this project is already deployed (by path or subdomain)

If phases 1-4 are not completed:
```
Infrastructure not ready. Complete these phases first:
  /stx-deploy:provision
  /stx-deploy:secure
  /stx-deploy:install-coolify
  /stx-deploy:configure-domain <domain>
```

### Step 3: Run preflight checks

Execute the same checks as `/stx-deploy:preflight` on the project:
- `book.py` exists
- `pyproject.toml` with streamtex
- `.streamlit/config.toml` with correct settings
- No sensitive files

If any required check fails, stop and report.

### Step 4: Ensure Dockerfile exists

If no Dockerfile in the project:
1. Generate one using the StreamTeX standard template:

```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true UV_LINK_MODE=copy
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["uv", "run", "streamlit", "run", "book.py", \
    "--server.port=8501", "--server.address=0.0.0.0", \
    "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
```

2. If `--folder` is specified (multi-manual), adjust ENTRYPOINT:
```dockerfile
ENV FOLDER=manuals/stx_manual_intro
ENTRYPOINT ["sh", "-c", "cd ${FOLDER} && uv run streamlit run book.py \
    --server.port=8501 --server.address=0.0.0.0 \
    --server.enableCORS=false --server.enableXsrfProtection=false"]
```

3. Create `.dockerignore` if absent:
```
.git
.venv
__pycache__
.pytest_cache
.ruff_cache
tests/
*.pyc
.env
```

### Step 5: Verify code is pushed to GitHub

```bash
git status
git log --oneline -1
git remote -v
```

If there are uncommitted changes, warn the user:
```
Warning: You have uncommitted changes. The deployment will use the
code on GitHub, not your local changes. Push first:
  git add -A && git commit -m "Prepare for deployment" && git push
```

If no remote is configured, help set one up.

### Step 6: Determine subdomain

If `--domain` not specified:
1. Extract project name from directory name
2. Get base domain from `.stx-deploy.json`
3. Subdomain = `{project-name}.{base-domain}`
4. Confirm with user

### Step 7: Configure in Coolify

Guide the user through Coolify UI (or use Coolify API if available):

```
In Coolify (https://coolify.$DOMAIN):

1. Projects → Add New → Name: "$PROJECT_NAME"
2. Add New Environment → Name: "production"
3. Add New Resource → Public Repository (or GitHub App)
4. Repository: $GITHUB_REPO
5. Branch: main
6. Build Pack: Dockerfile
7. Configuration:
   - Port Exposes: 8501
   - Domain: https://$SUBDOMAIN
8. Environment Variables:
   $ENV_VARS
9. Resource Limits:
   - Memory Limit: $MEMORY
   - CPU Limit: $CPU
10. Click "Deploy"
```

If using Coolify API:
```bash
# Create application via Coolify API
curl -X POST "https://coolify.$DOMAIN/api/v1/applications" \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_uuid": "...",
    "environment_name": "production",
    "type": "dockerfile",
    "name": "'$PROJECT_NAME'",
    "git_repository": "'$GITHUB_REPO'",
    "git_branch": "main",
    "ports_exposes": "8501",
    "domains": "'$SUBDOMAIN'"
  }'
```

### Step 8: Monitor deployment

```
Deployment started. Monitoring build logs...
```

Track the build progress in Coolify. Report:
- Build started
- Docker image building
- Container starting
- Health check passing

### Step 9: Verify deployment

```bash
# Check health
curl -s "https://$SUBDOMAIN/_stcore/health"
# Should return "ok"

# Check SSL
curl -sI "https://$SUBDOMAIN" | head -5
```

### Step 10: Configure auto-deploy webhook

Guide the user:
```
To enable auto-deploy on git push:

1. In Coolify, go to the application settings
2. Enable "Auto Deploy" → copy the Webhook URL
3. In GitHub: Settings → Webhooks → Add webhook
   - URL: (paste the webhook URL)
   - Content type: application/json
   - Events: Just the push event
4. Save
```

### Step 11: Update state file

Add the project to `.stx-deploy.json`:
```json
{
  "name": "cours-python",
  "path": "projects/cours-python",
  "github_repo": "username/cours-python",
  "subdomain": "cours-python.mondomaine.com",
  "server": "streamtex-prod",
  "memory_limit": "1g",
  "cpu_limit": "1.0",
  "status": "running",
  "deployed_at": "2026-03-19T15:00:00Z",
  "auto_deploy": true
}
```

### Step 12: Check CDN status

Read `.stx-deploy.json` and check if `cdn.enabled` is true.

If CDN is NOT configured, append a reminder:
```
Tip: Your server has no CDN or bot protection yet.
     Run /stx-deploy:configure-domain to set up Cloudflare (free).
```

### Step 13: Display result

```
Project deployed successfully!
  URL:     https://cours-python.mondomaine.com
  Status:  running (health check OK)
  Memory:  1g
  Auto-deploy: enabled
  CDN:     $CDN_STATUS

Deploy another: /stx-deploy:deploy [path]
Deploy batch:   /stx-deploy:deploy-batch [folder]
Check status:   /stx-deploy:status
```
