#!/usr/bin/env bash
# uvsync.sh — Ensure the correct Python version is installed and sync dependencies.
# Run this instead of `uv sync` on any machine to guarantee a reproducible environment.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_VERSION_FILE="$SCRIPT_DIR/.python-version"

if [[ ! -f "$PYTHON_VERSION_FILE" ]]; then
    echo "ERROR: .python-version not found in $SCRIPT_DIR" >&2
    exit 1
fi

PYTHON_VERSION="$(cat "$PYTHON_VERSION_FILE" | tr -d '[:space:]')"
echo "==> Target Python version: $PYTHON_VERSION"

# Update uv itself to ensure it knows about recent Python releases
echo "==> Updating uv..."
if uv self update 2>/dev/null; then
    echo "    uv updated successfully."
else
    echo "    WARNING: 'uv self update' failed (uv may have been installed via Homebrew or a package manager)."
    echo "    If Python installation fails below, update uv manually:"
    echo "      - Homebrew:  brew upgrade uv"
    echo "      - Standalone: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi
echo "    uv version: $(uv --version)"

# Install the exact Python version via uv (no-op if already present)
echo "==> Installing Python $PYTHON_VERSION (if not already installed)..."
uv python install "$PYTHON_VERSION"

# Pin the project to this version (updates .python-version — idempotent)
uv python pin "$PYTHON_VERSION"

# Sync all dependencies (creates/updates .venv)
echo "==> Syncing dependencies..."
uv sync

echo "==> Done. Environment ready with Python $PYTHON_VERSION."
