#!/usr/bin/env python3
"""
CCSP Casa 7 — Relatório Semanal (toda segunda, 8h BRT / 11h UTC)
Avisa o Alê que o relatório semanal está pronto para ser atualizado.
"""

import sys, os, json, requests
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))
hoje = datetime.now(BRT)
semana_str = hoje.strftime("%d/%m/%Y")

def gerar_alerta():
    return f"""📊 *CCSP Casa 7 — Atualização Semanal | {semana_str}*

Alê, preciso de 3 inputs para fechar o relatório desta semana:

*1. Cronograma atualizado do Victor*
  → Arquivo .mpp ou % de avanço por atividade

*2. Decisões e deliberações da semana*
  → O que o cliente (TOOLS/Rafael) aprovou, pediu ou questionou?
  → Alguma diretriz nova da gerenciadora?
  → Aprovações pendentes que foram resolvidas?

*3. Ocorrências novas*
  → Algum imprevisto, não conformidade ou desvio não registrado?

Com isso gero: relatório interno, relatório TOOLS, look ahead, alertas e histórico atualizado.

_Flávia | MIA Engenharia 🟢_"""

def enviar_telegram(mensagem):
    cfg_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(cfg_path) as f:
        cfg = json.load(f)
    
    telegram_token = cfg.get("channels", {}).get("telegram", {}).get("botToken")
    
    if not telegram_token:
        print("Token Telegram não encontrado", file=sys.stderr)
        return False
    
    r = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
        json={"chat_id": "1067279351", "text": mensagem, "parse_mode": "Markdown"},
        timeout=30
    )
    
    if r.status_code == 200:
        print(f"[{semana_str}] Alerta semanal CCSP enviado")
        return True
    else:
        print(f"Erro: {r.status_code} {r.text}", file=sys.stderr)
        return False

if __name__ == "__main__":
    msg = gerar_alerta()
    enviar_telegram(msg)
