# Deploying StreamTeX on Hugging Face Spaces

## Overview

| Aspect           | Details                                          |
|------------------|--------------------------------------------------|
| **Cost**         | Free (CPU Basic: 2 vCPU, 16 GB RAM)             |
| **Docker**       | Required (native Streamlit SDK is deprecated)     |
| **Custom domain**| Paid plans only (free: *.hf.space)               |
| **Sleep**        | Free tier apps may sleep after inactivity         |
| **Best for**     | ML demos, data apps, free hosting with Docker     |

## Prerequisites

1. A [Hugging Face](https://huggingface.co) account
2. `git` and `git-lfs` installed:
   ```bash
   # macOS
   brew install git git-lfs
   # Linux
   sudo apt install git git-lfs
   ```
3. HuggingFace CLI authenticated:
   ```bash
   pip install huggingface-hub
   huggingface-cli login
   ```
   Create a token with **Write** scope at: Settings → Access Tokens → New token

## Automated deployment

Use the deployment script:

```bash
# Deploy the default project (stx_manual_intro)
./deploy/huggingface.sh https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE

# Deploy a specific project
./deploy/huggingface.sh https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE projects/project_aiai18h
```

The script will:
1. Check prerequisites (git, git-lfs, HF token)
2. Run preflight checks (tests, config validation)
3. Configure the `hf` git remote
4. Set up Git LFS for large assets
5. Offer to push to HuggingFace

## Manual deployment

### 1. Create a Docker Space

1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Name your Space
3. Select **Docker** as the SDK
4. Choose **Blank** template
5. Create the Space

### 2. Configure the remote

```bash
git remote add hf https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE
```

### 3. Set up Git LFS

```bash
git lfs install
git lfs track "*.png" "*.jpg" "*.jpeg" "*.webp" "*.mp4" "*.gif" "*.svg"
```

### 4. Ensure README.md has HF front-matter

The top of your `README.md` must contain:

```yaml
---
title: StreamTeX
emoji: 🚀
colorFrom: red
colorTo: red
sdk: docker
app_port: 8501
tags:
- streamlit
pinned: false
short_description: Your app description
---
```

A template is available at `deploy/templates/hf-readme.yml`.

### 5. Push

```bash
git push hf main
```

HuggingFace auto-builds the Docker image and deploys. Monitor at your Space URL.

## Deploying a different project

The Dockerfile uses a `FOLDER` build-arg (default: `documentation/manuals/stx_manual_intro`).

To deploy a different project, you need to change the default in the Dockerfile before pushing:

```dockerfile
ARG FOLDER="projects/your_project"
```

Or configure HF Space build args in the Space settings.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check Space logs. Ensure `Dockerfile` is at repo root. |
| "No space disk left" | Remove large files from git history or use LFS. |
| App crashes on start | Check that `enableStaticServing = true` in `.streamlit/config.toml` |
| Images not loading | Ensure images are committed (not in `.gitignore`) and in `static/` |
| Push rejected | Run `git pull hf main --allow-unrelated-histories` first |

## Updating

Push changes to the `hf` remote:

```bash
git push hf main
```

HuggingFace rebuilds the Docker image automatically on each push.
