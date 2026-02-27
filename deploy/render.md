# Deploying StreamTeX on Render.com

## Overview

| Aspect           | Details                                          |
|------------------|--------------------------------------------------|
| **Cost**         | Free (750h/month) or $7/month (always-on)        |
| **Docker**       | Supported (also supports auto-detection)          |
| **Custom domain**| Yes (free and paid plans)                         |
| **Sleep**        | Free tier: sleeps after 15 min, cold start 30-60s |
| **Best for**     | Hobby projects, small production apps             |

## Prerequisites

1. A [Render.com](https://render.com) account (free, no credit card required)
2. The StreamTeX repo pushed to GitHub
3. Docker installed locally (optional, for testing)

## Automated deployment

Use the deployment script:

```bash
# Deploy the default project (stx_manual_intro)
./deploy/render.sh

# Deploy a specific project
./deploy/render.sh projects/project_aiai18h
```

The script will:
1. Run preflight checks (tests, config)
2. Validate `render.yaml`
3. Optionally build and test Docker locally
4. Guide you through the Render.com setup

## Manual deployment

### Option A: Blueprint (render.yaml)

The repo includes a `render.yaml` at the root that Render auto-detects:

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **New** → **Blueprint**
3. Connect your GitHub repo
4. Render reads `render.yaml` and creates the service
5. Click **Apply**

To change the deployed project, edit the `FOLDER` env var in `render.yaml`:

```yaml
envVars:
  - key: FOLDER
    value: projects/your_project    # Change this
```

### Option B: Manual setup

1. Go to [dashboard.render.com/new/web](https://dashboard.render.com/new/web)
2. Connect your GitHub repo
3. Configure:
   - **Name**: `streamtex` (or your choice)
   - **Runtime**: Docker
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Build Context Directory**: `.`
4. Add environment variable:
   - `FOLDER` = `projects/your_project` (or `documentation/manuals/stx_manual_intro`)
5. Set **Health Check Path**: `/_stcore/health`
6. Choose plan:
   - **Free**: 750 instance-hours/month, sleeps after 15 min
   - **Starter** ($7/month): Always-on, no sleep
7. Click **Create Web Service**

### Passing the FOLDER build-arg

Render supports Docker build args. The `FOLDER` env var in render.yaml is passed to the Docker build. If configuring manually, set it in the service's environment variables.

The Dockerfile uses it as:
```dockerfile
ARG FOLDER="documentation/manuals/stx_manual_intro"
```

## Free tier limitations

| Limitation | Details |
|------------|---------|
| Sleep | After 15 min without traffic, app sleeps |
| Cold start | 30-60 seconds to wake up |
| Hours | 750 instance-hours per month (31 days × 24h = 744h → fits one always-on app) |
| Bandwidth | 100 GB per month |
| Build | Free builds, but queued (paid builds are prioritized) |

For always-on apps, upgrade to the Starter plan ($7/month).

## Custom domain

1. Go to your service → **Settings** → **Custom Domains**
2. Add your domain
3. Render provides a CNAME record to configure at your DNS provider
4. SSL is auto-provisioned via Let's Encrypt

## Updating

Render auto-deploys on every push to the configured branch (default: `main`).

You can also trigger manual deploys from the dashboard.

## Deploying multiple projects

Create multiple services, each with a different `FOLDER` env var:

| Service | FOLDER | Port |
|---------|--------|------|
| streamtex-intro | `documentation/manuals/stx_manual_intro` | Auto |
| streamtex-advanced | `documentation/manuals/stx_manual_advanced` | Auto |
| streamtex-collection | `documentation/manuals/stx_manuals_collection` | Auto |

Each service gets its own URL (e.g., `streamtex-intro.onrender.com`).

## Password gate (STX_PASSWORD)

StreamTeX includes a visual password gate (`streamtex/auth.py`). The `STX_PASSWORD` environment variable plays a **dual role**: it activates the gate **and** defines the click sequence. Each character is uppercased and filtered to grid-valid chars (A-Z, 0-9).

| Scenario | Gate | Sequence |
|----------|------|----------|
| `STX_PASSWORD` not set or empty | Off | — |
| `STX_PASSWORD=hello` | On | Click **H → E → L → L → O** |
| `STX_PASSWORD=abc123` | On | Click **A → B → C → 1 → 2 → 3** |
| `STX_PASSWORD=hi!99` | On | Click **H → I → 9 → 9** (symbols filtered out) |
| `STX_GATE=1` (no password) | On (dev preview) | Default sequence |

### Password management workflow

The real password is stored in **`.env`** (git-ignored) and pushed to Render via a sync script. The `render.yaml` file contains only a `changeme` placeholder.

```
.env (local, git-ignored)          render.yaml (committed)
┌─────────────────────┐            ┌──────────────────────────────┐
│ STX_PASSWORD=yourpass│            │ value: changeme  # placeholder│
└─────────┬───────────┘            └──────────────────────────────┘
          │
          ▼
  deploy/sync-password.sh
          │
          ▼
  Render API (all services)
```

**Changing the password:**

1. Edit `STX_PASSWORD` in `.env`
2. Run `./deploy/sync-password.sh` to push to all Render services

```bash
# Edit .env
# STX_PASSWORD=yourpass

# Sync to Render
./deploy/sync-password.sh
#   ✓ streamtex (srv-xxx) → STX_PASSWORD updated
#   ✓ streamtex-intro (srv-yyy) → STX_PASSWORD updated
#   ...
```

**To disable the gate entirely**: remove `STX_PASSWORD` from `.env` and delete the variable from each service via the Render dashboard or API.

### Render CLI & API key

The Render CLI is installed via `brew install render`. After `render login`, the API key is stored in:

```
~/.render/cli.yaml
```

```yaml
api:
    key: rnd_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx    # ← API key for curl commands
    host: https://api.render.com/v1/
```

> **Note**: The CLI v2 has bugs in non-interactive (headless) mode.
> For scripting, prefer the REST API directly with the key from `cli.yaml`.

### Manual API update (alternative to sync-password.sh)

```bash
API_KEY=$(grep 'key:' ~/.render/cli.yaml | head -1 | awk '{print $2}')

# List all service IDs
curl -s -H "Authorization: Bearer $API_KEY" \
  "https://api.render.com/v1/services?limit=20" \
  | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    svc = s.get('service', s)
    print(f\"{svc['id']}  {svc['name']}\")
"

# Update a single service
curl -s -X PUT -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '[{"key":"STX_PASSWORD","value":"yourpass"}]' \
  "https://api.render.com/v1/services/<SERVICE_ID>/env-vars"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Render build logs. Ensure Dockerfile is at root. |
| "502 Bad Gateway" | App may be starting. Check health check path (`/_stcore/health`). |
| App sleeps too often | Upgrade to Starter plan, or use an external uptime monitor to ping the app. |
| Images not loading | Verify `enableStaticServing = true` in `.streamlit/config.toml` |
| Slow cold start | Normal for free tier (~30-60s). Docker image size affects this. |
| Out of free hours | One always-on app uses ~744h/month, which fits in the 750h free quota. Two apps won't fit. |
| Password unchanged after push | `render.yaml` contains a placeholder (`changeme`). Run `./deploy/sync-password.sh` to push the real password from `.env` to all services. See [Password gate](#password-gate-stx_password). |
