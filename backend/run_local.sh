#!/bin/zsh
export WORKSHOP_BACKEND_HOST="127.0.0.1"
export WORKSHOP_BACKEND_PORT="8765"
export WORKSHOP_BACKEND_ALLOW_ORIGIN="*"
poetry run python -m backend.app
