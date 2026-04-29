#!/usr/bin/env bash
set -euo pipefail
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SKILL_DIR"
exec "$SKILL_DIR/.venv/bin/python" scripts/instagram_analyzer.py "$@"
