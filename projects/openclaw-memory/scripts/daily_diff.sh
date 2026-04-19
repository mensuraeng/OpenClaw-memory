#!/bin/bash
# daily_diff.sh - O que mudou hoje? O que mudou na semana? Quais riscos cresceram?
# Uso: bash /root/.openclaw/workspace/projects/openclaw-memory/scripts/daily_diff.sh

REPO="/root/.openclaw/workspace/projects/openclaw-memory"
MEMORY="/root/.openclaw/workspace/memory"
CONTEXT="/root/.openclaw/workspace/memory/context"
TODAY=$(date +%Y-%m-%d)

echo "============================================================"
echo " OPENCLAW DAILY DIFF --- $TODAY"
echo "============================================================"

echo ""
echo "=== MUDANCAS 24H ==="
cd "$REPO" 2>/dev/null && git diff HEAD~1 --stat 2>/dev/null || echo "Sem commits anteriores"

echo ""
echo "=== MUDANCAS 7 DIAS ==="
cd "$REPO" 2>/dev/null && git log --oneline --since="7 days ago" 2>/dev/null || echo "Sem commits recentes"

echo ""
echo "=== DECISOES ATIVAS ==="
if [ -f "$CONTEXT/decisions.md" ]; then
    grep -B2 "\[ATIVA\]" "$CONTEXT/decisions.md" | grep "^### " | tail -5 | sed "s/^### /  - /"
else
    echo "  decisions.md nao encontrado"
fi

echo ""
echo "=== PENDENCIAS CRITICAS ==="
if [ -f "$CONTEXT/pending.md" ]; then
    grep -E "CRITICO|BLOQUEADO" "$CONTEXT/pending.md" 2>/dev/null | head -10 || echo "  Sem pendencias criticas"
else
    echo "  pending.md nao encontrado"
fi

echo ""
echo "=== RISCOS E ALERTAS (nota de hoje) ==="
DAILY_NOTE="$MEMORY/$TODAY.md"
if [ -f "$DAILY_NOTE" ]; then
    grep -iE "risco|alerta|urgente|critico|bloqueio" "$DAILY_NOTE" | head -8 || echo "  Sem alertas na nota de hoje"
else
    echo "  Nota do dia nao encontrada: $DAILY_NOTE"
fi

echo ""
echo "============================================================"