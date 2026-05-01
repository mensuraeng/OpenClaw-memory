#!/usr/bin/env bash
set -euo pipefail

# Rotina segura de snapshot da VPS Hostinger.
# Política:
# 1) versionar workspace no GitHub com falha explícita se push falhar;
# 2) criar backup criptografado do 2nd-brain no Backblaze B2;
# 3) criar backup full criptografado da VPS no Backblaze B2;
# 4) aplicar retenção segura, mantendo pelo menos 2 conjuntos externos recentes;
# 5) só então solicitar snapshot Hostinger, que sobrescreve o snapshot anterior.
# Nunca restaura nem apaga snapshot Hostinger.

WORKSPACE="/root/.openclaw/workspace"
RUNTIME_DIR="$WORKSPACE/runtime/hostinger"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOG="$RUNTIME_DIR/hostinger-vps-snapshot-$STAMP.log"
LATEST="$RUNTIME_DIR/hostinger-vps-snapshot-latest.log"
STATUS="$RUNTIME_DIR/hostinger-vps-snapshot-latest.json"
REMOTE_MIN_SETS=2

mkdir -p "$RUNTIME_DIR"
cd "$WORKSPACE"

exec > >(tee -a "$LOG") 2>&1
ln -sf "$LOG" "$LATEST"

json_status() {
  local status="$1"
  local message="$2"
  python3 - "$STATUS" "$status" "$message" "$LOG" <<'PY'
import json, sys
from datetime import datetime, timezone
path, status, message, log = sys.argv[1:5]
data = {
  "checked_at": datetime.now(timezone.utc).isoformat(),
  "status": status,
  "message": message,
  "log": log,
  "policy": {
    "hostinger_snapshot_slots": 1,
    "remote_min_safety_sets_before_snapshot": 2,
    "note": "Hostinger snapshot overwrites the previous slot; safety history is kept in B2/local backups."
  }
}
open(path, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
PY
}

on_error() {
  local rc=$?
  json_status "error" "Rotina abortada antes do snapshot Hostinger; ver log para causa."
  exit "$rc"
}
trap on_error ERR

echo "[$(date -Is)] Iniciando rotina segura de snapshot Hostinger"

# 1. Workspace -> GitHub, sem fallback silencioso.
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
  if ! git diff --cached --quiet; then
    git commit -m "chore: workspace backup before hostinger snapshot $(date '+%Y-%m-%d %H:%M:%S %z')"
  fi
fi

if git remote get-url origin >/dev/null 2>&1; then
  git push origin HEAD
fi

# 2. Backup 2nd-brain no B2.
python3 scripts/backup_2nd_brain_b2.py --run

# 3. Backup full VPS no B2.
python3 scripts/backup_vps_full_b2.py --run

# 4. Retenção segura B2/local.
RETENTION_JSON="$RUNTIME_DIR/backup-retention-$STAMP.json"
python3 scripts/backup_retention_b2.py --run > "$RETENTION_JSON"

# 5. Validar pelo menos 2 conjuntos remotos completos antes de sobrescrever Hostinger.
python3 - "$RETENTION_JSON" "$REMOTE_MIN_SETS" <<'PY'
import json, sys
path = sys.argv[1]
minimum = int(sys.argv[2])
with open(path, encoding='utf-8') as f:
    data = json.load(f)
vps = [s for s in data.get('plan', {}).get('remote_vps_sets', []) if s.get('complete')]
brain = [s for s in data.get('plan', {}).get('remote_2nd_brain_sets', []) if s.get('complete')]
if len(vps) < minimum or len(brain) < minimum:
    raise SystemExit(f'Backup remoto insuficiente antes do snapshot: vps={len(vps)} 2nd-brain={len(brain)} mínimo={minimum}')
print(json.dumps({'remote_safety_sets_ok': True, 'vps_sets': len(vps), 'second_brain_sets': len(brain), 'minimum': minimum}, ensure_ascii=False))
PY

# 6. Criar snapshot Hostinger.
python3 scripts/hostinger_snapshot_create.py --yes --json

json_status "ok" "Snapshot Hostinger solicitado após backup GitHub+B2 e validação de pelo menos 2 conjuntos remotos."
echo "[$(date -Is)] Rotina concluída"
