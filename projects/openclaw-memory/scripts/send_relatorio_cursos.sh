#!/bin/bash
# Relatório semanal de cursos via curadoria LLM (relatorio_cursos.py).
# Pós-FASE 5: NÃO fala mais com Telegram diretamente.
# Gera o relatório e entrega como payload à Flávia, que decide a saída.
# Não tem cron — wrapper para uso manual.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

REPORT_FILE="$(mktemp)"
trap 'rm -f "$REPORT_FILE"' EXIT

echo "📚 Gerando relatório de cursos via LLM..." >&2
python3 "$SCRIPT_DIR/relatorio_cursos.py" > "$REPORT_FILE"

echo "📨 Entregando à Flávia..." >&2
python3 - "$REPORT_FILE" <<'PYEOF'
import json, os, sys
from datetime import datetime
sys.path.insert(0, "/root/.openclaw/workspace/scripts")
from send_to_flavia import send_to_flavia

with open(sys.argv[1], encoding="utf-8") as f:
    body = f.read()

payload = {
    "source": "send_relatorio_cursos.sh",
    "kind": "relatorio_semanal_cursos_llm",
    "project": None,
    "company": None,
    "domain": "formacao_profissional",
    "urgency": "low",
    "scheduled_at": datetime.now().isoformat(),
    "body": body,
}
sys.exit(send_to_flavia(payload))
PYEOF
