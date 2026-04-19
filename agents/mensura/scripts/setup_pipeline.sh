#!/bin/bash
# setup_pipeline.sh — Setup idempotente do pipeline MPP -> Relatorio Preditivo
# Uso: bash setup_pipeline.sh
# VPS: 76.13.161.249 | Ubuntu 24.04 | Python 3.12 | Java 21

set -e

SCRIPTS_DIR="/root/.openclaw/workspace/agents/mensura/scripts"
MEM_DIR="/root/.openclaw/workspace/memory/obras"
TMP_DIR="/tmp/openclaw_reports"
REQUIREMENTS="$SCRIPTS_DIR/requirements.txt"

echo "=============================================="
echo "  SETUP — Pipeline MPP -> Relatorio Preditivo"
echo "  MENSURA Engenharia | $(date '+%Y-%m-%d %H:%M')"
echo "=============================================="

# 1. Diretorios
echo "[1/5] Criando diretorios..."
mkdir -p "$SCRIPTS_DIR" "$MEM_DIR" "$TMP_DIR"
echo "      OK: $SCRIPTS_DIR"
echo "      OK: $MEM_DIR"
echo "      OK: $TMP_DIR"

# 2. Java
echo "[2/5] Verificando Java..."
if java -version 2>&1 | grep -q "openjdk"; then
    JAVA_VER=$(java -version 2>&1 | grep -oP '(?<=version ")\d+')
    echo "      OK: Java $JAVA_VER encontrado"
else
    echo "      Instalando Java 21..."
    apt-get update -qq
    apt-get install -y default-jre
    echo "      OK: Java instalado"
fi

# 3. Python deps fixadas
echo "[3/5] Instalando dependencias Python fixadas..."
if [ -f "$REQUIREMENTS" ]; then
    pip install -r "$REQUIREMENTS" --break-system-packages -q
    echo "      OK: mpxj==16.1.0, JPype1==1.7.0 (fixadas via requirements.txt)"
else
    echo "      AVISO: requirements.txt nao encontrado, instalando versoes padrao..."
    pip install mpxj==16.1.0 JPype1==1.7.0 --break-system-packages -q
fi

# 4. Permissoes
echo "[4/5] Ajustando permissoes..."
chmod +x "$SCRIPTS_DIR"/*.sh 2>/dev/null || true
chmod +x "$SCRIPTS_DIR"/*.py 2>/dev/null || true
echo "      OK: scripts executaveis"

# 5. Verificacao final
echo "[5/5] Verificando ambiente..."
python3 "$SCRIPTS_DIR/verify_env.py"

echo "=============================================="
echo "  SETUP CONCLUIDO COM SUCESSO!"
echo "  Use: bash $SCRIPTS_DIR/relatorio_semanal_auto.sh <arquivo.mpp> <nome_obra>"
echo "=============================================="
