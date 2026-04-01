#!/bin/bash
# Relatório semanal de cursos - envia via Telegram
CHAT_ID="1067279351"
BOT_TOKEN=$(python3 -c "import json; d=json.load(open('/root/.openclaw/openclaw.json')); print(d['channels']['telegram']['botToken'])")

python3 /root/.openclaw/workspace/scripts/relatorio_cursos.py | while IFS= read -r -d '' chunk; do
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
        -d "chat_id=${CHAT_ID}" \
        -d "text=${chunk}" \
        -d "parse_mode=Markdown" > /dev/null
done
