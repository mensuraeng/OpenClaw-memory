#!/usr/bin/env python3
"""
CCSP Casa 7 — Cobrança RDO às 16h30 BRT (19h30 UTC)
Roda seg-sex
Envia Telegram para o Alê + e-mail direto ao Victor (cc Alexandre e André)
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

def enviar_email_rdo(mensagem_texto):
    cfg_path = os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json")
    with open(cfg_path) as f:
        cfg = json.load(f)

    token_resp = requests.post(
        f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token",
        data={'grant_type': 'client_credentials', 'client_id': cfg['clientId'],
              'client_secret': cfg['clientSecret'], 'scope': 'https://graph.microsoft.com/.default'}
    )
    token = token_resp.json()['access_token']

    linhas = mensagem_texto.replace("*", "").split("\n")
    html_linhas = []
    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("✅"):
            html_linhas.append(f"<li>{linha}</li>")
        elif linha == "":
            html_linhas.append("<br>")
        else:
            html_linhas.append(f"<p style='margin:4px 0'>{linha}</p>")
    html_body = "\n".join(html_linhas)

    email_body = {
        "message": {
            "subject": f"CCSP Casa 7 — RDO Pendente | {dia_str}",
            "body": {
                "contentType": "HTML",
                "content": f"""<div style="font-family:Arial,sans-serif;font-size:14px;color:#1a1a1a;max-width:600px">
{html_body}
</div>"""
            },
            "toRecipients": [
                {"emailAddress": {"address": "victor.evangelista@miaengenharia.com.br"}}
            ],
            "ccRecipients": [
                {"emailAddress": {"address": "alexandre@miaengenharia.com.br"}},
                {"emailAddress": {"address": "andre@miaengenharia.com.br"}}
            ]
        },
        "saveToSentItems": True
    }

    resp = requests.post(
        "https://graph.microsoft.com/v1.0/users/flavia@mensuraengenharia.com.br/sendMail",
        json=email_body,
        headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    )
    if resp.status_code in (200, 202):
        print(f"[{dia_str}] E-mail RDO enviado ao Victor")
        return True
    else:
        print(f"Erro e-mail: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return False


if __name__ == "__main__":
    msg = gerar_mensagem_rdo()
    enviar_telegram(msg)
    enviar_email_rdo(msg)
