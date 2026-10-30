#!/bin/zsh
# Local preview of the backend with sample analytics, for following design work.
# Opens the admin dashboard at http://127.0.0.1:8765/admin (PREVIEW_PORT=8766 to change) (credentials: backend/.env,
# or admin / preview when no .env exists).
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PREVIEW_PORT="${PREVIEW_PORT:-${WORKSHOP_BACKEND_PORT:-8765}}"
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  . "$SCRIPT_DIR/.env"
  set +a
fi

export WORKSHOP_BACKEND_HOST="127.0.0.1"
export WORKSHOP_BACKEND_PORT="$PREVIEW_PORT"
export WORKSHOP_ENABLE_ADMIN_ANALYTICS=true
export WORKSHOP_ADMIN_USERNAME="${WORKSHOP_ADMIN_USERNAME:-admin}"
export WORKSHOP_ADMIN_PASSWORD="${WORKSHOP_ADMIN_PASSWORD:-preview}"
export WORKSHOP_ANALYTICS_FILE="$SCRIPT_DIR/data/demo-analytics.jsonl"

cd "$SCRIPT_DIR/.."
poetry run python -m backend.demo_analytics "$WORKSHOP_ANALYTICS_FILE"
echo "Admin preview: http://127.0.0.1:$WORKSHOP_BACKEND_PORT/admin"
exec poetry run python -m backend.app
