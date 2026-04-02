#!/usr/bin/env python3
"""
CCSP Casa 7 — Cobrança RDO às 16h30 BRT (19h30 UTC)
Roda seg-sex
"""

import sys, os, json, requests
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))
hoje = datetime.now(BRT)
dia_str = hoje.strftime("%d/%m/%Y")
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"]
dia_nome = DIAS[hoje.weekday()]

def gerar_mensagem_rdo():
    return f"""⏰ *CCSP Casa 7 — Cobrança RDO | {dia_str}*

Victor, o RDO de hoje ({dia_str}) ainda não foi enviado ou precisa ser conferido.

*Checklist rápido para fechar o dia:*
  ✅ RDO preenchido (mesmo que parcial)
  ✅ Fotos do avanço do dia anexadas
  ✅ Não conformidades registradas com descrição
  ✅ Pendências do dia documentadas no grupo
  ✅ Insumos/materiais que faltam para amanhã levantados

Enviar antes de sair da obra.

_Flávia | MIA Engenharia 🟢_"""

def enviar_telegram(mensagem):
    cfg_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(cfg_path) as f:
        cfg = json.load(f)
    
    telegram_token = cfg.get("channels", {}).get("telegram", {}).get("botToken")
    
    if not telegram_token:
        print("Token Telegram não encontrado", file=sys.stderr)
        return False
    
    texto = f"Cobrança RDO — encaminhar ao Victor:\n\n{mensagem}"
    
    r = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
        json={"chat_id": "1067279351", "text": texto, "parse_mode": "Markdown"},
        timeout=30
    )
    
    if r.status_code == 200:
        print(f"[{dia_str}] Cobrança RDO enviada com sucesso")
        return True
    else:
        print(f"Erro Telegram: {r.status_code} {r.text}", file=sys.stderr)
        return False

if __name__ == "__main__":
    msg = gerar_mensagem_rdo()
    enviar_telegram(msg)
