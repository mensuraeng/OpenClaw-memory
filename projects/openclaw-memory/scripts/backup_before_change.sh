#!/usr/bin/env bash
set -euo pipefail

LABEL="${1:-structural-change}"
OUT_DIR="/root/openclaw-backups"
META_FILE="/root/.openclaw/workspace/backups/latest-structural-backup.json"
mkdir -p "$OUT_DIR" "$(dirname "$META_FILE")"

TMP_JSON="$(mktemp)"
openclaw backup create --verify --no-include-workspace --output "$OUT_DIR" --json > "$TMP_JSON"
GIT_COMMIT="$(git -C /root/.openclaw/workspace rev-parse HEAD 2>/dev/null || true)"
python3 - <<'PY' "$TMP_JSON" "$META_FILE" "$LABEL" "$GIT_COMMIT"
import json, sys, pathlib
src, dst, label, git_commit = sys.argv[1:5]
data = json.loads(pathlib.Path(src).read_text())
data['label'] = label
data['workspaceGitCommit'] = git_commit or None
path = pathlib.Path(dst)
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print(path.read_text())
PY
rm -f "$TMP_JSON"
