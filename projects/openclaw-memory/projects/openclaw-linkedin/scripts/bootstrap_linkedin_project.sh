#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

mkdir -p "$ROOT/docs" "$ROOT/config" "$ROOT/scripts" "$ROOT/templates" "$ROOT/examples"

if [[ ! -f "$ROOT/.gitignore" ]]; then
  cat > "$ROOT/.gitignore" <<'EOF'
.env
.env.*
secrets/
*.log
.DS_Store
EOF
fi

echo "OpenClaw LinkedIn Operations bootstrap ok: $ROOT"
