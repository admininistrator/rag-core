#!/bin/sh
set -eu

API_PORT="${1:-8000}"
BASE_URL="http://127.0.0.1:$API_PORT"

LIVE_JSON=$(curl -s -f --max-time 10 "$BASE_URL/health/live")
READY_JSON=$(curl -s -f --max-time 10 "$BASE_URL/health/ready")

python3 -c "
import sys, json

live = json.loads('''$LIVE_JSON''')
if live.get('status') != 'ok':
    sys.exit('Liveness status was not ok')

ready = json.loads('''$READY_JSON''')
if ready.get('status') != 'ready':
    sys.exit('Readiness status was not ready')

components = ready.get('components', {})
for name in ('postgres', 'redis', 'qdrant'):
    if components.get(name) != 'ok':
        sys.exit(f'Readiness component {name} was not ok')
"

echo "PASS /health/live status=ok"
echo "PASS /health/ready status=ready components=postgres,redis,qdrant"

