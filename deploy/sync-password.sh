#!/usr/bin/env bash
# deploy/sync-password.sh — Sync STX_PASSWORD from .env to all Render services
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT_DIR/.env"

# 1. Read STX_PASSWORD from .env
if [ ! -f "$ENV_FILE" ]; then
    echo "✗ .env not found at $ENV_FILE"; exit 1
fi
PASSWORD=$(grep '^STX_PASSWORD=' "$ENV_FILE" | cut -d= -f2-)
if [ -z "$PASSWORD" ]; then
    echo "✗ STX_PASSWORD not set in .env"; exit 1
fi

# 2. Read Render API key
CLI_YAML="$HOME/.render/cli.yaml"
if [ ! -f "$CLI_YAML" ]; then
    echo "✗ ~/.render/cli.yaml not found — run 'render login' first"; exit 1
fi
API_KEY=$(grep 'key:' "$CLI_YAML" | head -1 | awk '{print $2}')

# 3. List services
SERVICES=$(curl -s -H "Authorization: Bearer $API_KEY" \
    "https://api.render.com/v1/services?limit=50")

# 4. Update each service
echo "$SERVICES" | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    svc = s.get('service', s)
    print(f\"{svc['id']}  {svc['name']}\")
" | while read -r SVC_ID SVC_NAME; do
    curl -s -X PUT -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "[{\"key\":\"STX_PASSWORD\",\"value\":\"$PASSWORD\"}]" \
        "https://api.render.com/v1/services/$SVC_ID/env-vars" > /dev/null
    echo "  ✓ $SVC_NAME ($SVC_ID) → STX_PASSWORD updated"
done

echo ""
echo "Done. All services updated with STX_PASSWORD from .env."
