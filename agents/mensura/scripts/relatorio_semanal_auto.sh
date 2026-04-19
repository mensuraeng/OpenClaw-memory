#!/bin/bash
# relatorio_semanal_auto.sh — Wrapper para pipeline de relatorio automatico
# Uso: ./relatorio_semanal_auto.sh <caminho.mpp> <nome_obra>
# Cron sugerido: toda segunda 7:05 BRT (10:05 UTC)
# Exemplo crontab: 5 10 * * 1 /root/.openclaw/workspace/agents/mensura/scripts/relatorio_semanal_auto.sh /path/obra.mpp "Nome Obra"

MPP_FILE=$1
OBRA_NAME=$2
SCRIPTS_DIR="/root/.openclaw/workspace/agents/mensura/scripts"
TMP_DIR="/tmp/openclaw_reports"
DATE=$(date +%Y%m%d)

if [ -z "$MPP_FILE" ] || [ -z "$OBRA_NAME" ]; then
    echo "Uso: $0 <caminho.mpp> <nome_obra>"
    exit 1
fi

if [ ! -f "$MPP_FILE" ]; then
    echo "ERRO: Arquivo nao encontrado: $MPP_FILE"
    exit 1
fi

mkdir -p "$TMP_DIR"

echo "[$(date)] Iniciando pipeline para: $OBRA_NAME"
echo "[$(date)] Arquivo: $MPP_FILE"

# 1. Extrai dados do .mpp
echo "[$(date)] Passo 1/2 - Extraindo dados do .mpp..."
python3 "$SCRIPTS_DIR/extract_schedule.py" "$MPP_FILE" --obra "$OBRA_NAME" --out "$TMP_DIR/${OBRA_NAME// /_}_${DATE}.json"

if [ $? -ne 0 ]; then
    echo "[$(date)] ERRO na extracao do .mpp"
    exit 2
fi

# 2. Gera prompt e salva KPIs na memoria
echo "[$(date)] Passo 2/2 - Gerando prompt e salvando KPIs..."
python3 "$SCRIPTS_DIR/generate_report.py"     --json "$TMP_DIR/${OBRA_NAME// /_}_${DATE}.json"     --obra "$OBRA_NAME"     --memoria     --out "$TMP_DIR/${OBRA_NAME// /_}_${DATE}_prompt.txt"

if [ $? -ne 0 ]; then
    echo "[$(date)] ERRO na geracao do prompt"
    exit 3
fi

echo "[$(date)] ========================"
echo "[$(date)] Pipeline concluido com sucesso!"
echo "[$(date)] JSON: $TMP_DIR/${OBRA_NAME// /_}_${DATE}.json"
echo "[$(date)] Prompt: $TMP_DIR/${OBRA_NAME// /_}_${DATE}_prompt.txt"
echo "[$(date)] KPIs salvos na memoria OpenClaw"
echo "[$(date)] Envie o prompt para o skill relatorio-preditivo-obras."
