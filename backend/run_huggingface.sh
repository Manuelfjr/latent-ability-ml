#!/bin/sh
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  . "$SCRIPT_DIR/.env"
  set +a
fi

export WORKSHOP_BACKEND_HOST="0.0.0.0"
export WORKSHOP_BACKEND_PORT="${PORT:-7860}"
export WORKSHOP_BACKEND_ALLOW_ORIGIN="${WORKSHOP_BACKEND_ALLOW_ORIGIN:-*}"
export WORKSHOP_ENABLE_ADMIN_ANALYTICS="${WORKSHOP_ENABLE_ADMIN_ANALYTICS:-false}"
poetry run python -m backend.app
