#!/usr/bin/env bash
# deploy/gen-requirements.sh — Generate requirements.txt from pyproject.toml
#
# Streamlit Community Cloud does not support uv or pyproject.toml natively.
# This script generates a classic requirements.txt for compatibility.
#
# Usage:
#   ./deploy/gen-requirements.sh                    # Output to stdout
#   ./deploy/gen-requirements.sh > requirements.txt # Save to file

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$ROOT_DIR"

# Check uv is available
if ! command -v uv &>/dev/null; then
    echo "ERROR: uv is not installed. Install it first: https://docs.astral.sh/uv/" >&2
    exit 1
fi

# Export production dependencies only (no dev group)
uv export --no-dev --no-hashes --frozen 2>/dev/null | grep -v "^#" | grep -v "^-e" | grep -v "^$"
