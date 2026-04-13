#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/root/.openclaw/workspace"
cd "$REPO_DIR"

if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add -A
  git commit -m "chore: workspace backup $(date '+%Y-%m-%d %H:%M:%S %z')" || true
fi

if git remote get-url origin >/dev/null 2>&1; then
  git push origin HEAD || true
fi
