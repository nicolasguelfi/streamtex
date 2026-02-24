#!/usr/bin/env bash
# deploy/huggingface.sh — Deploy a StreamTeX project to Hugging Face Spaces
#
# Usage:
#   ./deploy/huggingface.sh <HF_SPACE_URL> [PROJECT_FOLDER]
#
# Examples:
#   ./deploy/huggingface.sh https://huggingface.co/spaces/myuser/my-space
#   ./deploy/huggingface.sh https://huggingface.co/spaces/myuser/my-space projects/project_aiai18h
#
# Prerequisites:
#   - git and git-lfs installed
#   - huggingface-hub CLI: pip install huggingface-hub (or uv add huggingface-hub)
#   - HF token with Write scope (run: huggingface-cli login)
#   - A Docker Space created on huggingface.co

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}▸${NC} $1"; }
pass()  { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "  ${RED}✗${NC} $1"; exit 1; }

# ── Parse arguments ───────────────────────────────────────
HF_SPACE_URL="${1:-}"
PROJECT_FOLDER="${2:-documentation/manuals/stx_manual_intro}"

if [ -z "$HF_SPACE_URL" ]; then
    echo "Usage: ./deploy/huggingface.sh <HF_SPACE_URL> [PROJECT_FOLDER]"
    echo ""
    echo "Example:"
    echo "  ./deploy/huggingface.sh https://huggingface.co/spaces/myuser/my-space"
    echo "  ./deploy/huggingface.sh https://huggingface.co/spaces/myuser/my-space projects/my_project"
    exit 1
fi

echo "═══════════════════════════════════════════════════════"
echo " StreamTeX → Hugging Face Spaces Deployment"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Space:   $HF_SPACE_URL"
echo "  Project: $PROJECT_FOLDER"
echo ""

# ── Pre-flight checks ────────────────────────────────────
info "Checking prerequisites..."

# Git
if command -v git &>/dev/null; then
    pass "git installed"
else
    fail "git is not installed"
fi

# Git LFS
if git lfs version &>/dev/null; then
    pass "git-lfs installed"
else
    fail "git-lfs is not installed (brew install git-lfs)"
fi

# HF CLI login check
if [ -f "$HOME/.cache/huggingface/token" ] || [ -n "${HF_TOKEN:-}" ]; then
    pass "HuggingFace token found"
else
    warn "No HF token detected. Run: huggingface-cli login"
fi

# Project folder
if [ -d "$ROOT_DIR/$PROJECT_FOLDER" ] && [ -f "$ROOT_DIR/$PROJECT_FOLDER/book.py" ]; then
    pass "Project folder valid ($PROJECT_FOLDER)"
else
    fail "Invalid project folder: $PROJECT_FOLDER (must contain book.py)"
fi

# Dockerfile
if [ -f "$ROOT_DIR/Dockerfile" ]; then
    pass "Dockerfile found"
else
    fail "Dockerfile not found at repo root"
fi

echo ""

# ── Run pre-deployment checks ────────────────────────────
info "Running preflight checks..."
if "$SCRIPT_DIR/preflight.sh" "$PROJECT_FOLDER"; then
    pass "Preflight checks passed"
else
    fail "Preflight checks failed — fix before deploying"
fi
echo ""

# ── Configure HF remote ──────────────────────────────────
info "Configuring HuggingFace remote..."
cd "$ROOT_DIR"

# Add or update the 'hf' remote
if git remote get-url hf &>/dev/null; then
    CURRENT_URL=$(git remote get-url hf)
    if [ "$CURRENT_URL" = "$HF_SPACE_URL" ]; then
        pass "Remote 'hf' already configured"
    else
        git remote set-url hf "$HF_SPACE_URL"
        pass "Remote 'hf' updated to $HF_SPACE_URL"
    fi
else
    git remote add hf "$HF_SPACE_URL"
    pass "Remote 'hf' added: $HF_SPACE_URL"
fi

# ── Initialize Git LFS ───────────────────────────────────
info "Configuring Git LFS for large assets..."
git lfs install --local 2>/dev/null || true
git lfs track "*.png" "*.jpg" "*.jpeg" "*.webp" "*.mp4" "*.gif" "*.svg" 2>/dev/null || true
pass "LFS tracking configured"
echo ""

# ── Verify Dockerfile build-arg ──────────────────────────
info "Verifying Dockerfile..."
if grep -q "ARG FOLDER=" "$ROOT_DIR/Dockerfile"; then
    pass "Dockerfile supports FOLDER build-arg"
else
    warn "Dockerfile may not support FOLDER build-arg"
fi

# Check that README.md has HF front-matter
if head -5 "$ROOT_DIR/README.md" | grep -q "sdk: docker"; then
    pass "README.md has HuggingFace YAML front-matter"
else
    warn "README.md missing HF YAML front-matter (Space may not configure correctly)"
    echo ""
    echo "  Add this to the top of README.md:"
    echo "  ---"
    echo "  title: StreamTeX"
    echo "  sdk: docker"
    echo "  app_port: 8501"
    echo "  ---"
fi
echo ""

# ── Push ──────────────────────────────────────────────────
info "Ready to push to HuggingFace Space"
echo ""
echo "  To deploy, run:"
echo -e "    ${GREEN}git push hf main${NC}"
echo ""
echo "  HuggingFace will auto-build the Docker image and deploy."
echo "  Monitor at: $HF_SPACE_URL"
echo ""

# Ask for confirmation
read -p "Push now? [y/N] " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "Pushing to HuggingFace..."
    git push hf main
    echo ""
    pass "Push complete! Monitor deployment at:"
    echo "  $HF_SPACE_URL"
else
    echo ""
    echo "Skipped. Run 'git push hf main' when ready."
fi
