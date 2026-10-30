#!/bin/sh
# Publish the backend to the Hugging Face Space.
#
# main is the source of truth. This copies the runtime files from the current commit
# into the hf-backend branch (which keeps the Space README/metadata) and commits there.
#
#   ./backend/sync_hf_space.sh          # commit on hf-backend only
#   ./backend/sync_hf_space.sh --push   # also push hf-backend to the Space (hf/main)
set -eu

ROOT="$(git rev-parse --show-toplevel)"
SOURCE_REF="$(git -C "$ROOT" rev-parse --short HEAD)"
PATHS="backend utils notebooks src Dockerfile .dockerignore pyproject.toml requirements.txt"

if [ -n "$(git -C "$ROOT" status --porcelain -- $PATHS)" ]; then
  echo "Uncommitted changes in: $PATHS" >&2
  echo "Commit them first; the Space is built from HEAD ($SOURCE_REF)." >&2
  exit 1
fi

WORKTREE="$(mktemp -d)"
trap 'git -C "$ROOT" worktree remove --force "$WORKTREE" >/dev/null 2>&1 || true' EXIT
git -C "$ROOT" worktree add --quiet "$WORKTREE" hf-backend

cd "$WORKTREE"
# Remove first so files deleted on main also disappear from the Space.
git rm -r -q --ignore-unmatch $PATHS
git -C "$ROOT" archive HEAD $PATHS | tar -x -C "$WORKTREE"
git add -A $PATHS

if git diff --cached --quiet; then
  echo "hf-backend already matches $SOURCE_REF."
else
  git commit -q -m "Sync backend from main@$SOURCE_REF"
  echo "Committed on hf-backend:"
  git log --oneline -1
  git diff --stat HEAD~1 HEAD | tail -1
fi

if [ "${1:-}" = "--push" ]; then
  git push hf hf-backend:main
else
  echo "Not pushed. Run with --push to deploy to the Space."
fi
