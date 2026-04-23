#!/bin/bash
# relatorio_semanal_auto.sh — Wrapper para pipeline de relatorio automatico
# Uso: ./relatorio_semanal_auto.sh <caminho.mpp> <nome_obra>
# Cron sugerido: toda segunda 7:05 BRT (10:05 UTC)
# Exemplo crontab: 5 10 * * 1 /root/.openclaw/workspace/agents/mensura/scripts/relatorio_semanal_auto.sh /path/obra.mpp "Nome Obra"
#
# Dependencias: Java 21+, Python 3.10+, mpxj==16.1.0, JPype1==1.7.0
# Setup:        bash /root/.openclaw/workspace/agents/mensura/scripts/setup_pipeline.sh
# Verificacao:  python3 /root/.openclaw/workspace/agents/mensura/scripts/verify_env.py

set -euo pipefail

MPP_FILE="${1:-}"
OBRA_NAME="${2:-}"
SCRIPTS_DIR="/root/.openclaw/workspace/agents/mensura/scripts"
TMP_DIR="/tmp/openclaw_reports"
DATE=$(date +%Y%m%d_%H%M)
LOG_DIR="/root/.openclaw/workspace/memory/obras"
LOG_FILE="$LOG_DIR/pipeline_$(date +%Y%m%d).log"

# --- Funcoes utilitarias ---
log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }
err() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERRO: $1" | tee -a "$LOG_FILE" >&2; }

# --- Validacao de argumentos ---
if [ -z "$MPP_FILE" ] || [ -z "$OBRA_NAME" ]; then
    echo "Uso: $0 <caminho.mpp> <nome_obra>"
    echo ""
    echo "Exemplos:"
    echo "  $0 /root/obras/residencial.mpp 'Edificio Central'"
    echo "  $0 /root/obras/comercial.mpp 'Shopping Norte'"
    exit 1
fi

if [ ! -f "$MPP_FILE" ]; then
    err "Arquivo nao encontrado: $MPP_FILE"
    exit 1
fi

# --- Setup de diretorios ---
mkdir -p "$TMP_DIR" "$LOG_DIR"

OBRA_SLUG="${OBRA_NAME// /_}"
JSON_OUT="$TMP_DIR/${OBRA_SLUG}_${DATE}.json"
PROMPT_OUT="$TMP_DIR/${OBRA_SLUG}_${DATE}_prompt.txt"

log "======================================================"
log "Iniciando pipeline para: $OBRA_NAME"
log "Arquivo: $MPP_FILE"
log "======================================================"

# --- PREFLIGHT: Verificar dependencias criticas ---
log "Preflight: verificando dependencias..."

# Java
if ! java -version 2>&1 | grep -q "openjdk\|java version"; then
    err "Java nao encontrado. Execute: bash $SCRIPTS_DIR/setup_pipeline.sh"
    exit 2
fi

# mpxj versao fixada
MPXJ_INSTALLED=$(pip show mpxj 2>/dev/null | grep "^Version:" | awk '{print $2}')
MPXJ_REQUIRED="16.1.0"
if [ "$MPXJ_INSTALLED" != "$MPXJ_REQUIRED" ]; then
    err "mpxj $MPXJ_INSTALLED instalado, requer $MPXJ_REQUIRED fixada."
    err "Corrija: pip install mpxj==$MPXJ_REQUIRED --break-system-packages"
    exit 2
fi

log "Preflight OK: Java + mpxj $MPXJ_INSTALLED validados"

# --- PASSO 1: Extrair dados do .mpp ---
log "Passo 1/2 — Extraindo dados do .mpp..."
if ! python3 "$SCRIPTS_DIR/extract_schedule.py" "$MPP_FILE" --obra "$OBRA_NAME" --out "$JSON_OUT" 2>>"$LOG_FILE"; then
    err "Falha na extracao do .mpp. Verifique o log: $LOG_FILE"
    exit 3
fi
log "JSON extraido: $JSON_OUT ($(wc -c < "$JSON_OUT") bytes)"

# --- PASSO 2: Gerar prompt + salvar KPIs na memoria ---
log "Passo 2/2 — Gerando prompt e salvando KPIs na memoria..."
if ! python3 "$SCRIPTS_DIR/generate_report.py" \
        --json "$JSON_OUT" \
        --obra "$OBRA_NAME" \
        --memoria \
        --out "$PROMPT_OUT" 2>>"$LOG_FILE"; then
    err "Falha na geracao do prompt. Verifique o log: $LOG_FILE"
    exit 4
fi

log "======================================================"
log "PIPELINE CONCLUIDO COM SUCESSO!"
log "  JSON:   $JSON_OUT"
log "  Prompt: $PROMPT_OUT"
log "  KPIs:   /root/.openclaw/workspace/memory/obras/${OBRA_SLUG,,}-kpis.json"
log "  Log:    $LOG_FILE"
log "======================================================"
log "Proximo passo: cole o conteudo do prompt no skill relatorio-preditivo-obras."
