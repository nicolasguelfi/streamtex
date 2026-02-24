# StreamTeX Deployment Guide

This directory contains scripts, configuration files, and documentation for deploying StreamTeX projects to various platforms.

## Quick comparison

| Platform | Cost | Docker | Custom domain | Sleep | Best for |
|----------|------|--------|---------------|-------|----------|
| **Docker local** | $0 | Yes | N/A | No | Development, testing |
| **Streamlit Cloud** | $0 | No | No | 12h | Quick demos, prototyping |
| **HuggingFace Spaces** | $0 | Yes | Paid | Yes | Free hosting with Docker |
| **Render.com** | $0-7/mo | Yes | Yes | 15 min (free) | Production, hobby projects |
| **GCP VM + Ansible** | ~$5-25/mo | Optional | Yes | No | Full control, multi-project |

## Decision matrix

| I want to... | Use |
|---------------|-----|
| Test locally with Docker | `docker compose up` |
| Share a quick demo for free | Streamlit Community Cloud |
| Host a free app with Docker | HuggingFace Spaces |
| Deploy to production with custom domain | Render.com |
| Control everything on my own server | GCP VM + Ansible |

## Prerequisites (all platforms)

Before deploying, run the preflight checks:

```bash
./deploy/preflight.sh                                    # General checks
./deploy/preflight.sh projects/your_project              # Project-specific checks
```

This verifies: tests pass, `enableStaticServing = true`, static assets exist, git is clean.

---

## Option 1: Docker local

Run one or more projects locally using Docker.

### Single project

```bash
docker build --build-arg FOLDER=projects/your_project -t streamtex-app .
docker run -p 8501:8501 streamtex-app
# Open http://localhost:8501
```

### Multiple projects (docker compose)

```bash
docker compose up --build          # Build & run all 3 demo projects
docker compose up --build intro    # Run only the intro project
docker compose down                # Stop everything
```

| Service | URL | Project |
|---------|-----|---------|
| collection | http://localhost:8501 | stx_manuals_collection |
| intro | http://localhost:8502 | stx_manual_intro |
| advanced | http://localhost:8503 | stx_manual_advanced |

**Files**: `Dockerfile`, `docker-compose.yml`, `.dockerignore`

---

## Option 2: Streamlit Community Cloud

Free hosting on Streamlit's managed platform. No Docker needed.

```bash
./deploy/gen-requirements.sh > requirements.txt    # Generate requirements.txt
# Commit and push to GitHub
# Connect repo at share.streamlit.io
```

**Documentation**: [deploy/streamlit-cloud.md](streamlit-cloud.md)

**Files**: `deploy/gen-requirements.sh`, `deploy/streamlit-cloud.md`

---

## Option 3: HuggingFace Spaces

Free Docker-based hosting on HuggingFace.

```bash
./deploy/huggingface.sh https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE
./deploy/huggingface.sh https://huggingface.co/spaces/YOUR_USER/YOUR_SPACE projects/your_project
```

**Documentation**: [deploy/huggingface.md](huggingface.md)

**Files**: `deploy/huggingface.sh`, `deploy/huggingface.md`, `deploy/templates/hf-readme.yml`

---

## Option 4: Render.com

Production-ready hosting with free tier and custom domains.

```bash
./deploy/render.sh                         # Deploy default project
./deploy/render.sh projects/your_project   # Deploy specific project
```

**Documentation**: [deploy/render.md](render.md)

**Files**: `render.yaml` (at repo root), `deploy/render.sh`, `deploy/render.md`

---

## Option 5: GCP VM + Ansible

Full control on a Google Cloud VM with automated provisioning via Ansible.

```bash
# 1. Copy and configure inventory
cp deploy/ansible/inventory.ini.example deploy/ansible/inventory.ini
# Edit inventory.ini with your VM IP and username

# 2. Edit deploy.yml with your project details
# Edit deploy/ansible/deploy.yml

# 3. Deploy
ansible-playbook -i deploy/ansible/inventory.ini deploy/ansible/deploy.yml
```

**Files**: `deploy/ansible/inventory.ini.example`, `deploy/ansible/deploy.yml`

---

## CI/CD

GitHub Actions workflow runs automatically on push/PR:

- **On every push/PR**: lint + tests
- **On push to main**: Docker build + health check verification

**File**: `.github/workflows/ci.yml`

---

## File inventory

```
deploy/
├── README.md                  # This file
├── preflight.sh               # Pre-deployment checks (used by all scripts)
├── gen-requirements.sh        # Generate requirements.txt for Streamlit Cloud
├── streamlit-cloud.md         # Streamlit Community Cloud documentation
├── huggingface.sh             # HuggingFace Spaces deployment script
├── huggingface.md             # HuggingFace Spaces documentation
├── render.sh                  # Render.com deployment script
├── render.md                  # Render.com documentation
├── templates/
│   └── hf-readme.yml          # HuggingFace Space README template
└── ansible/
    ├── inventory.ini.example  # Ansible inventory template
    └── deploy.yml             # Ansible playbook for GCP VM

Root files:
├── Dockerfile                 # Multi-project Docker build
├── .dockerignore              # Docker build exclusions
├── docker-compose.yml         # Multi-project local Docker
├── render.yaml                # Render.com IaC configuration
└── .github/workflows/ci.yml  # GitHub Actions CI/CD
```
