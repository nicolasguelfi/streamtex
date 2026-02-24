#!/usr/bin/env bash
# deploy/render.sh — Deploy a StreamTeX project to Render.com
#
# Usage:
#   ./deploy/render.sh [PROJECT_FOLDER]
#
# Examples:
#   ./deploy/render.sh                                    # Deploy default (intro manual)
#   ./deploy/render.sh projects/project_aiai18h           # Deploy a specific project
#
# This script:
#   1. Runs preflight checks
#   2. Validates render.yaml
#   3. Verifies Docker build works locally
#   4. Guides you through Render.com setup

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

PROJECT_FOLDER="${1:-documentation/manuals/stx_manual_intro}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${CYAN}▸${NC} $1"; }
pass()  { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "  ${RED}✗${NC} $1"; exit 1; }

echo "═══════════════════════════════════════════════════════"
echo " StreamTeX → Render.com Deployment"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  Project: $PROJECT_FOLDER"
echo ""

# ── Preflight checks ─────────────────────────────────────
info "Running preflight checks..."
if "$SCRIPT_DIR/preflight.sh" "$PROJECT_FOLDER"; then
    pass "Preflight checks passed"
else
    fail "Preflight checks failed — fix before deploying"
fi
echo ""

# ── Validate render.yaml ─────────────────────────────────
info "Checking render.yaml..."
if [ -f "$ROOT_DIR/render.yaml" ]; then
    pass "render.yaml found"

    # Check if it references the right Dockerfile
    if grep -q "dockerfilePath: ./Dockerfile" "$ROOT_DIR/render.yaml"; then
        pass "render.yaml references Dockerfile"
    else
        warn "render.yaml may not reference the correct Dockerfile"
    fi
else
    fail "render.yaml not found at repo root"
fi
echo ""

# ── Verify Dockerfile ────────────────────────────────────
info "Checking Dockerfile..."
if [ -f "$ROOT_DIR/Dockerfile" ]; then
    pass "Dockerfile found"
else
    fail "Dockerfile not found at repo root"
fi

# ── Optional: local Docker build test ────────────────────
info "Testing Docker build locally..."
echo ""
read -p "  Build Docker image locally to verify? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    info "Building Docker image..."
    cd "$ROOT_DIR"
    if docker build --build-arg FOLDER="$PROJECT_FOLDER" -t streamtex-render-test . ; then
        pass "Docker build succeeded"
        echo ""

        read -p "  Run locally to test? [y/N] " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            info "Starting container on http://localhost:8501 ..."
            echo "  Press Ctrl+C to stop"
            docker run --rm -p 8501:8501 streamtex-render-test
        fi
    else
        fail "Docker build failed — fix before deploying to Render"
    fi
fi
echo ""

# ── Render.com setup instructions ─────────────────────────
echo "═══════════════════════════════════════════════════════"
echo " Next steps: Deploy on Render.com"
echo "═══════════════════════════════════════════════════════"
echo ""
echo "  1. Go to https://dashboard.render.com/new/web"
echo "  2. Connect your GitHub repo"
echo "  3. Render auto-detects render.yaml"
echo "     OR manually configure:"
echo "       - Runtime: Docker"
echo "       - Dockerfile path: ./Dockerfile"
echo "       - Docker build context: ."
echo "  4. Add environment variable:"
echo -e "       ${GREEN}FOLDER${NC} = ${CYAN}$PROJECT_FOLDER${NC}"
echo "  5. Set health check path: /_stcore/health"
echo "  6. Choose plan: Free ($0) or Starter (\$7/month)"
echo "  7. Click Deploy"
echo ""
echo "  Your app will be available at:"
echo "    https://streamtex-XXXX.onrender.com"
echo ""
echo "  Auto-deploys on push to main branch."
echo "═══════════════════════════════════════════════════════"
