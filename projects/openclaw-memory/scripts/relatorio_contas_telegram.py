#!/usr/bin/env python3
"""
Relatório semanal de contas a pagar — formata saída para o Telegram.
"""

import json, os, sys, subprocess
from datetime import datetime

CONTAS_FILE = os.path.expanduser("~/.openclaw/workspace/memory/contas_pagar.json")


def load_contas():
    if os.path.exists(CONTAS_FILE):
        with open(CONTAS_FILE) as f:
            return json.load(f)
    return {"contas": [], "pagos": []}


def formatar_relatorio():
    # Primeiro roda o scan
    result = subprocess.run(
        ["python3", os.path.expanduser("~/.openclaw/workspace/scripts/contas_pagar.py"), "scan"],
        capture_output=True, text=True
    )

    contas_data = load_contas()
    pendentes = [c for c in contas_data["contas"] if c.get("status") == "pendente"]

    hoje = datetime.now().strftime("%d/%m/%Y")
    linhas = [f"💰 *CONTAS A PAGAR — {hoje}*\n"]

    if not pendentes:
        linhas.append("✅ Nenhuma conta pendente identificada esta semana.")
    else:
        linhas.append(f"*{len(pendentes)} conta(s) pendente(s):*\n")
        for c in pendentes:
            venc = c.get("vencimento") or "⚠️ sem data"
            valor = c.get("valor") or "?"
            barcode = c.get("codigo_barras")
            desc = c.get("descricao", "Conta")[:60]
            conta_label = "Mensura" if "mensura" in c.get("conta", "").lower() else "MIA"
            evento = "📅 na agenda" if c.get("evento_id") else "⚠️ sem evento na agenda"

            linhas.append(f"📄 *{desc}*")
            linhas.append(f"   🏢 {conta_label} | 📆 Vence: {venc} | 💵 R$ {valor}")
            if barcode:
                linhas.append(f"   🔑 `{barcode}`")
            else:
                linhas.append(f"   🔑 Código não identificado automaticamente")
            linhas.append(f"   {evento}\n")

    linhas.append("─────────────────────")
    linhas.append("Após pagar cada conta, me manda o comprovante que dou baixa. ✅")

    return "\n".join(linhas)


if __name__ == "__main__":
    print(formatar_relatorio())
