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
    return f"""📊 *CCSP Casa 7 — Relatório Semanal | {semana_str}*

Alê, é hora de atualizar o acompanhamento da Casa 7.

Para gerar o relatório atualizado, me mande o cronograma atualizado do Victor (arquivo .mpp ou os dados de % avanço por atividade).

Com os dados, gero:
  • Análise de desvio (Previsto x Realizado)
  • Look Ahead das próximas 2 semanas
  • Alertas de risco atualizados
  • Relatório HTML completo
  • Mensagem de cobrança para o Victor

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
