# Deploying StreamTeX on Streamlit Community Cloud

## Overview

| Aspect           | Details                                          |
|------------------|--------------------------------------------------|
| **Cost**         | Free (up to ~3 apps)                             |
| **Docker**       | Not supported                                    |
| **Custom domain**| Not supported (*.streamlit.app only)             |
| **Sleep**        | Apps sleep after ~12h without traffic             |
| **Best for**     | Quick demos, prototyping, public sharing          |

## Limitations

- No Docker support — requires `requirements.txt`
- No custom domains
- ~1 GB RAM per app
- Apps go to sleep after inactivity (cold start on wake)
- GitHub repo must be public (or you need admin permissions for private repos)
- US-only hosting

## Prerequisites

1. A GitHub account
2. The StreamTeX repo pushed to GitHub (public or with admin access)
3. A [Streamlit Community Cloud](https://streamlit.io/cloud) account (free, link your GitHub)

## Step-by-step

### 1. Generate requirements.txt

Streamlit Cloud does not support `uv` or `pyproject.toml`. Generate a classic `requirements.txt`:

```bash
./deploy/gen-requirements.sh > requirements.txt
```

Commit this file to the repo.

### 2. Create the app on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repo
4. Set the **Main file path** to your project's entry point:
   - Example: `documentation/manuals/stx_manual_intro/book.py`
   - Or: `projects/your_project/book.py`
5. Optionally set **Python version** to `3.13` (or leave default)
6. Click **Deploy**

### 3. Configuration

Streamlit Cloud reads `.streamlit/config.toml` from your project folder automatically.
Make sure `enableStaticServing = true` is set (it should already be).

Some config values are overridden by Streamlit Cloud:
- `server.headless` is forced to `true`
- `server.port` is managed by the platform
- `browser.gatherUsageStats` may be overridden

### 4. Verify

Your app will be available at:
```
https://<your-app-name>.streamlit.app
```

## Updating

Push changes to your GitHub repo. Streamlit Cloud auto-deploys on push to the configured branch.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| App crashes on deploy | Check Streamlit Cloud logs (visible in the dashboard) |
| Images not loading | Verify `enableStaticServing = true` and images are in `static/` |
| "No module named streamtex" | Ensure `streamtex/` is at the repo root and importable |
| Dependency conflict | Regenerate `requirements.txt` with `./deploy/gen-requirements.sh` |
