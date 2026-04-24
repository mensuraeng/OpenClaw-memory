#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="/root/.openclaw/workspace"
cd "$REPO_DIR"

# Nunca versionar artefatos transitórios ou repositórios embutidos por engano.
git reset -q HEAD -- projects/claw3d 2>/dev/null || true
git reset -q HEAD -- marketing 2>/dev/null || true
git reset -q HEAD -- 'projects/mission-control/data/*.db-wal' 'projects/mission-control/data/*.db-shm' 2>/dev/null || true
git reset -q HEAD -- 'projects/mission-control/src/components/TenacitOS/*.bak-kanban' 2>/dev/null || true

if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
  git add -A
  git restore --staged projects/claw3d 2>/dev/null || true
  git restore --staged marketing 2>/dev/null || true
  git restore --staged 'projects/mission-control/data/*.db-wal' 'projects/mission-control/data/*.db-shm' 2>/dev/null || true
  git restore --staged 'projects/mission-control/src/components/TenacitOS/*.bak-kanban' 2>/dev/null || true
  git commit -m "chore: workspace backup $(date '+%Y-%m-%d %H:%M:%S %z')" || true
fi

if git remote get-url origin >/dev/null 2>&1; then
  git push origin HEAD || true
fi
