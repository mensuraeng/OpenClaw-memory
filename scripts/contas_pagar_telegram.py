#!/usr/bin/env python3
"""
Relatório semanal de contas a pagar.
Roda toda segunda-feira às 10h BRT (cron 0 13 * * 1).

Pós-FASE 5: NÃO fala mais com Telegram diretamente.
Fluxo:
1. roda contas_pagar.py scan (escaneia emails Mensura+MIA buscando boletos)
2. carrega memory/contas_pagar.json
3. monta payload para Flávia
4. entrega via send_to_flavia.py — domínio FINANCEIRO,
   Flávia decide se delega para o agente `finance` ou resolve direta

Flags:
  --skip-scan         pula a etapa de scan (usa o JSON atual)
  --skip-flavia       imprime relatório no stdout em vez de entregar
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

CONTAS_FILE = os.path.expanduser("~/.openclaw/workspace/memory/contas_pagar.json")
SCAN_SCRIPT = os.path.expanduser("~/.openclaw/workspace/scripts/contas_pagar.py")


def load_contas() -> dict:
    if os.path.exists(CONTAS_FILE):
        with open(CONTAS_FILE) as f:
            return json.load(f)
    return {"contas": [], "pagos": []}


def run_scan() -> int:
    """Executa o scan de emails para detectar novas contas."""
    try:
        result = subprocess.run(
            ["python3", SCAN_SCRIPT, "scan"],
            capture_output=True, text=True, timeout=180,
        )
        if result.stdout:
            sys.stderr.write(result.stdout)
        if result.returncode != 0:
            sys.stderr.write(f"Scan stderr: {result.stderr}\n")
        return result.returncode
    except subprocess.TimeoutExpired:
        sys.stderr.write("Timeout no scan de contas\n")
        return 1


def formatar_relatorio(contas_data: dict) -> str:
    pendentes = [c for c in contas_data.get("contas", []) if c.get("status") == "pendente"]
    pagos_recentes = contas_data.get("pagos", [])

    hoje = datetime.now().strftime("%d/%m/%Y")
    linhas = [f"💰 *CONTAS A PAGAR — {hoje}*\n"]

    if not pendentes:
        linhas.append("✅ Nenhuma conta pendente identificada esta semana. Tudo em dia!")
    else:
        linhas.append(f"*{len(pendentes)} conta(s) pendente(s):*\n")
        for c in pendentes:
            venc = c.get("vencimento") or "⚠️ não identificado"
            valor = c.get("valor") or "não identificado"
            barcode = c.get("codigo_barras")
            desc = (c.get("descricao") or "Conta")[:60]
            conta_label = "Mensura" if "mensura" in (c.get("conta") or "").lower() else "MIA"
            evento = "📅 na agenda" if c.get("evento_id") else "⚠️ sem evento na agenda"

            linhas.append(f"📄 *{desc}*")
            linhas.append(f"🏢 {conta_label}  |  📆 Vence: {venc}  |  💵 R$ {valor}")
            if barcode:
                linhas.append(f"🔑 `{barcode}`")
            else:
                linhas.append("🔑 Código não identificado automaticamente")
            linhas.append(f"{evento}\n")

    linhas.append("─────────────────────")
    linhas.append("Após pagar, manda o comprovante que dou baixa. ✅")

    if pagos_recentes:
        linhas.append(f"\n_Histórico: {len(pagos_recentes)} conta(s) já paga(s) registrada(s)_")

    return "\n".join(linhas)


def calcular_urgency(contas_data: dict) -> str:
    """high se tem pendente vencendo em <=3 dias; normal se há pendentes; low se nenhum."""
    pendentes = [c for c in contas_data.get("contas", []) if c.get("status") == "pendente"]
    if not pendentes:
        return "low"
    hoje = datetime.now().date()
    for c in pendentes:
        venc = c.get("vencimento")
        if not venc:
            continue
        try:
            # tenta dd/mm/yyyy
            d = datetime.strptime(venc, "%d/%m/%Y").date()
        except ValueError:
            try:
                d = datetime.strptime(venc, "%Y-%m-%d").date()
            except ValueError:
                continue
        if (d - hoje).days <= 3:
            return "high"
    return "normal"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-scan", action="store_true",
                        help="Pula scan de emails; usa o JSON existente")
    parser.add_argument("--skip-flavia", action="store_true",
                        help="Imprime relatório no stdout em vez de entregar à Flávia")
    args = parser.parse_args()

    if not args.skip_scan:
        sys.stderr.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Escaneando emails...\n")
        run_scan()

    contas_data = load_contas()
    relatorio_texto = formatar_relatorio(contas_data)

    if args.skip_flavia:
        print(relatorio_texto)
        return 0

    pendentes = [c for c in contas_data.get("contas", []) if c.get("status") == "pendente"]
    pagos = contas_data.get("pagos", [])

    payload = {
        "source": "contas_pagar_telegram.py",
        "kind": "relatorio_contas_a_pagar",
        "project": None,
        "company": None,
        "domain": "financeiro",
        "urgency": calcular_urgency(contas_data),
        "scheduled_at": datetime.now().isoformat(),
        "totals": {
            "pendentes": len(pendentes),
            "pagos_historico": len(pagos),
        },
        "body": relatorio_texto,
        "raw": {
            "pendentes": pendentes,
        },
    }
    return send_to_flavia(payload)


if __name__ == "__main__":
    sys.exit(main())
