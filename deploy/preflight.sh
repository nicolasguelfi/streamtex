#!/usr/bin/env bash
# deploy/preflight.sh — Pre-deployment checks common to all targets
#
# Usage:
#   ./deploy/preflight.sh [PROJECT_FOLDER]
#
# Runs checks that every deployment target requires:
#   1. Tests pass (uv run pytest)
#   2. enableStaticServing = true in .streamlit/config.toml
#   3. Static image assets exist (if referenced)
#   4. Git working tree is clean (warning only)
#   5. Streamlit version >= 1.54.0 in pyproject.toml
#
# Exit codes:
#   0 — All checks passed
#   1 — Critical check failed (tests, config)
#   2 — Warning-only issues (git dirty)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_FOLDER="${1:-}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

WARNINGS=0
ERRORS=0

pass()    { echo -e "  ${GREEN}✓${NC} $1"; }
warn()    { echo -e "  ${YELLOW}⚠${NC} $1"; WARNINGS=$((WARNINGS + 1)); }
fail()    { echo -e "  ${RED}✗${NC} $1"; ERRORS=$((ERRORS + 1)); }

echo "═══════════════════════════════════════════════════════"
echo " StreamTeX Pre-Deployment Checks"
echo "═══════════════════════════════════════════════════════"
echo ""

# ── 1. Run tests ──────────────────────────────────────────
echo "▸ Running tests..."
cd "$ROOT_DIR"
if uv run pytest tests/ -v --tb=short 2>&1; then
    pass "All tests passed"
else
    fail "Tests failed — fix before deploying"
fi
echo ""

# ── 2. Check Streamlit version requirement ────────────────
echo "▸ Checking Streamlit version..."
if grep -q 'streamlit>=1.54.0' "$ROOT_DIR/pyproject.toml" 2>/dev/null; then
    pass "streamlit>=1.54.0 in pyproject.toml"
else
    fail "streamlit>=1.54.0 not found in pyproject.toml"
fi

# ── 3. Check project config (if project folder given) ────
if [ -n "$PROJECT_FOLDER" ]; then
    PROJECT_PATH="$ROOT_DIR/$PROJECT_FOLDER"
    echo ""
    echo "▸ Checking project: $PROJECT_FOLDER"

    # book.py exists
    if [ -f "$PROJECT_PATH/book.py" ]; then
        pass "book.py found"
    else
        fail "book.py not found in $PROJECT_FOLDER"
    fi

    # .streamlit/config.toml exists and has enableStaticServing
    CONFIG_FILE="$PROJECT_PATH/.streamlit/config.toml"
    if [ -f "$CONFIG_FILE" ]; then
        if grep -q "enableStaticServing.*=.*true" "$CONFIG_FILE" 2>/dev/null; then
            pass "enableStaticServing = true"
        else
            fail "enableStaticServing is not set to true in $CONFIG_FILE"
        fi
    else
        fail ".streamlit/config.toml not found in $PROJECT_FOLDER"
    fi

    # Static images directory
    STATIC_DIR="$PROJECT_PATH/static"
    if [ -d "$STATIC_DIR" ]; then
        IMAGE_COUNT=$(find "$STATIC_DIR" -type f \( -name "*.png" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.svg" -o -name "*.webp" -o -name "*.gif" \) 2>/dev/null | wc -l | tr -d ' ')
        pass "static/ directory found ($IMAGE_COUNT image files)"
    else
        warn "No static/ directory in $PROJECT_FOLDER (OK if project has no assets)"
    fi
fi

# ── 4. Git status ─────────────────────────────────────────
echo ""
echo "▸ Checking git status..."
cd "$ROOT_DIR"
if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    pass "Working tree is clean"
else
    CHANGED=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    warn "Git has $CHANGED uncommitted change(s) — consider committing before deploying"
fi

# ── Summary ───────────────────────────────────────────────
echo ""
echo "═══════════════════════════════════════════════════════"
if [ "$ERRORS" -gt 0 ]; then
    echo -e " ${RED}FAILED${NC}: $ERRORS error(s), $WARNINGS warning(s)"
    echo " Fix errors before deploying."
    echo "═══════════════════════════════════════════════════════"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo -e " ${YELLOW}PASSED WITH WARNINGS${NC}: $WARNINGS warning(s)"
    echo "═══════════════════════════════════════════════════════"
    exit 0
else
    echo -e " ${GREEN}ALL CHECKS PASSED${NC}"
    echo "═══════════════════════════════════════════════════════"
    exit 0
fi
