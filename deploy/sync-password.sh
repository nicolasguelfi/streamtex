#!/usr/bin/env bash
# deploy/sync-password.sh — Sync STX_PASSWORD from .env to all Render services
#
# Render Blueprint auto-deploys overwrite env vars from render.yaml on every push.
# This script must run AFTER a deploy completes to set the real password.
#
# Safe approach: GET existing env vars → merge STX_PASSWORD → PUT full list → deploy.
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
echo "STX_PASSWORD read from .env (${#PASSWORD} chars)"

# 2. Read Render API key
CLI_YAML="$HOME/.render/cli.yaml"
if [ ! -f "$CLI_YAML" ]; then
    echo "✗ ~/.render/cli.yaml not found — run 'render login' first"; exit 1
fi
API_KEY=$(grep 'key:' "$CLI_YAML" | head -1 | awk '{print $2}')

# 3. List services
SERVICES=$(curl -s -H "Authorization: Bearer $API_KEY" \
    "https://api.render.com/v1/services?limit=50")

SVC_LIST=$(echo "$SERVICES" | python3 -c "
import sys, json
for s in json.load(sys.stdin):
    svc = s.get('service', s)
    print(f\"{svc['id']}  {svc['name']}\")
")

# 4. For each service: GET env vars → merge STX_PASSWORD → PUT back
echo ""
echo "Updating env vars..."
echo "$SVC_LIST" | while read -r SVC_ID SVC_NAME; do
    CURRENT=$(curl -s -H "Authorization: Bearer $API_KEY" \
        "https://api.render.com/v1/services/$SVC_ID/env-vars")

    MERGED=$(python3 -c "
import json, sys
env_list = json.loads(sys.argv[1])
result = {e['envVar']['key']: e['envVar']['value'] for e in env_list}
result['STX_PASSWORD'] = sys.argv[2]
print(json.dumps([{'key': k, 'value': v} for k, v in result.items()]))
" "$CURRENT" "$PASSWORD")

    curl -s -X PUT -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        -d "$MERGED" \
        "https://api.render.com/v1/services/$SVC_ID/env-vars" > /dev/null
    echo "  ✓ $SVC_NAME → env updated"
done

# 5. Trigger a deploy on each service (picks up new env vars reliably)
echo ""
echo "Triggering deploys..."
echo "$SVC_LIST" | while read -r SVC_ID SVC_NAME; do
    RESULT=$(curl -s -X POST -H "Authorization: Bearer $API_KEY" \
        -H "Content-Type: application/json" \
        "https://api.render.com/v1/services/$SVC_ID/deploys" 2>&1)
    DEP_ID=$(echo "$RESULT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    dep = d.get('deploy', d)
    print(dep.get('id', '?'))
except: print('?')" 2>/dev/null)
    echo "  ✓ $SVC_NAME → deploy $DEP_ID triggered"
done

# 6. Wait for deploys to go live
echo ""
echo "Waiting for deploys to finish (this takes 3-6 minutes)..."
ALL_LIVE=false
for i in $(seq 1 40); do
    sleep 10
    STILL_BUILDING=0
    echo "$SVC_LIST" | while read -r SVC_ID SVC_NAME; do
        STATUS=$(curl -s -H "Authorization: Bearer $API_KEY" \
            "https://api.render.com/v1/services/$SVC_ID/deploys?limit=1" \
            | python3 -c "
import sys, json
d = json.load(sys.stdin)
dep = d[0].get('deploy', d[0]) if d else {}
print(dep.get('status', 'unknown'))" 2>/dev/null)
        if [ "$STATUS" = "live" ]; then
            echo "  ✓ $SVC_NAME → live"
        else
            echo "  … $SVC_NAME → $STATUS"
            echo "BUILDING" > /tmp/_stx_sync_building
        fi
    done
    if [ ! -f /tmp/_stx_sync_building ]; then
        ALL_LIVE=true
        break
    fi
    rm -f /tmp/_stx_sync_building
done
rm -f /tmp/_stx_sync_building

echo ""
if [ "$ALL_LIVE" = true ]; then
    echo "Done. All services deployed with the real STX_PASSWORD."
else
    echo "Done. Some services may still be deploying — check the Render dashboard."
fi
