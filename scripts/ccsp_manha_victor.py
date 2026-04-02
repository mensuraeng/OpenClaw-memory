#!/usr/bin/env python3
"""
CCSP Casa 7 — Mensagem matinal para Victor Evangelista
Roda seg-sex às 8h BRT (11h UTC)
Gera mensagem baseada no cronograma, envia para o Alê via Telegram
e envia por e-mail diretamente ao Victor (com cópia para Alexandre e André)
"""

import sys, os, json, requests, base64
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))
hoje = datetime.now(BRT)
dia_semana = hoje.weekday()  # 0=seg, 4=sex
dia_str = hoje.strftime("%d/%m/%Y")

# Mapeamento dia da semana
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
dia_nome = DIAS[dia_semana]

# ============================================================
# BASE DE DADOS — atualizar semanalmente com o cronograma
# ============================================================
# Estrutura: data_iso -> lista de atividades esperadas
ATIVIDADES = {
    "2026-04-07": [
        "🔴 PRAZO CRÍTICO — Enviar mapa de custos de exaustores",
        "🔴 PRAZO CRÍTICO — Enviar mapa de custos de pintura",
        "🔴 PRAZO CRÍTICO — Enviar mapa mini-guias + batedores da garagem",
        "🔴 Enviar orçamento de película UV",
        "🔴 Enviar 3 orçamentos gesso/drywall",
        "Iniciar elétrica Banho Casal + Suíte Casal",
        "RDO do dia antes das 15h",
    ],
    "2026-04-08": [
        "Recomposição do baldrame — DIA 1",
        "Elétrica Banho Casal em andamento",
        "RDO do dia antes das 15h",
    ],
    "2026-04-09": [
        "Recomposição do baldrame — DIA 2 (CONCLUSÃO)",
        "✅ Meta: Conclusão Suíte 3",
        "RDO do dia antes das 15h",
    ],
    "2026-04-10": [
        "Impermeabilização externa — DIA 1",
        "✅ Meta: Conclusão Banho 03, Suíte 2, Banho 02, Suíte 1",
        "RDO do dia antes das 15h",
    ],
    "2026-04-13": [
        "Impermeabilização externa — DIA 2 (CONCLUSÃO)",
        "Acompanhar aprovação TOOLS (elétrica, exaustores, pintura, mini-guia)",
        "RDO do dia antes das 15h",
    ],
    "2026-04-14": [
        "✅ Meta: Conclusão Banho 01 + Circulação Íntima",
        "Rodapé argamassado área externa — DIA 1",
        "Mobilização pintura + mobilização limpeza geral",
        "RDO do dia antes das 15h",
    ],
    "2026-04-15": [
        "Rodapé área externa — DIA 2 (CONCLUSÃO)",
        "✅ Meta: Área externa concluída (baldrame + impermeabilização + rodapé)",
        "Dormitório 4 — preparação",
        "RDO do dia antes das 15h",
    ],
    "2026-04-16": [
        "✅ Meta: Instalação dos exaustores",
        "Dormitório 4 — execução checklist",
        "RDO do dia antes das 15h",
    ],
    "2026-04-17": [
        "✅ Meta: Conclusão Dormitório 4, Banho 4, Cozinha, Área de Serviço",
        "Mobilização pintura confirmada para segunda 20/04",
        "RDO do dia antes das 15h",
    ],
    "2026-04-20": [
        "🔴 PINTURA INICIA HOJE — acompanhar mobilização",
        "Área externa: verificar drenagem (conclusão prevista 24/04)",
        "RDO do dia antes das 15h",
    ],
}

# Prazos críticos sempre presentes
PRAZOS_CRITICOS = {
    "2026-04-07": "🔴 HOJE: prazo para envio dos mapas ao TOOLS",
    "2026-04-20": "🔴 HOJE: pintura deve iniciar",
}

# ============================================================
def gerar_mensagem():
    hoje_iso = hoje.strftime("%Y-%m-%d")
    
    atividades = ATIVIDADES.get(hoje_iso, [
        "Executar checklist dos ambientes em andamento conforme cronograma",
        "Registrar avanço físico do dia com fotos",
        "RDO do dia antes das 15h",
    ])
    
    prazo_critico = PRAZOS_CRITICOS.get(hoje_iso, "")
    
    lista = "\n".join(f"  • {a}" for a in atividades)
    
    msg = f"""*📋 CCSP Casa 7 — {dia_nome}, {dia_str}*

Bom dia, Victor! Segue o alinhamento do dia:

*Atividades previstas:*
{lista}

*Lembretes permanentes:*
  • RDO diário antes das 15h — obrigatório
  • Documentar todas as não conformidades com foto no grupo
  • Qualquer imprevisto ou desvio de prazo → comunicar imediatamente

{"⚠️ " + prazo_critico if prazo_critico else ""}

_Qualquer dúvida ou impedimento, avise logo cedo._
_Flávia | MIA Engenharia 🟢_"""
    
    return msg.strip()

# ============================================================
# Enviar para Alê via Telegram (ele encaminha para Victor)
# ============================================================
def enviar_telegram(mensagem):
    cfg_path = os.path.expanduser("~/.openclaw/openclaw.json")
    with open(cfg_path) as f:
        cfg = json.load(f)
    
    # Pegar token do Telegram
    telegram_token = cfg.get("channels", {}).get("telegram", {}).get("botToken")
    
    if not telegram_token:
        print("Token Telegram não encontrado", file=sys.stderr)
        return False
    
    chat_id = "1067279351"
    texto = f"Mensagem pronta para encaminhar ao Victor:\n\n{mensagem}"
    
    r = requests.post(
        f"https://api.telegram.org/bot{telegram_token}/sendMessage",
        json={"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"},
        timeout=30
    )
    
    if r.status_code == 200:
        print(f"[{dia_str}] Mensagem matinal enviada com sucesso")
        return True
    else:
        print(f"Erro Telegram: {r.status_code} {r.text}", file=sys.stderr)
        return False

# ============================================================
# Enviar e-mail ao Victor (com cópia para Alexandre e André)
# ============================================================
def enviar_email(mensagem_texto):
    cfg_path = os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json")
    with open(cfg_path) as f:
        cfg = json.load(f)

    token_resp = requests.post(
        f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token",
        data={'grant_type': 'client_credentials', 'client_id': cfg['clientId'],
              'client_secret': cfg['clientSecret'], 'scope': 'https://graph.microsoft.com/.default'}
    )
    token = token_resp.json()['access_token']

    # Converter bullet points para HTML
    linhas = mensagem_texto.replace("*", "").split("\n")
    html_linhas = []
    for linha in linhas:
        linha = linha.strip()
        if linha.startswith("•"):
            html_linhas.append(f"<li>{linha[1:].strip()}</li>")
        elif linha == "":
            html_linhas.append("<br>")
        else:
            html_linhas.append(f"<p style='margin:4px 0'>{linha}</p>")
    html_body = "\n".join(html_linhas)

    assunto = f"CCSP Casa 7 — Alinhamento do Dia | {dia_str}"

    email_body = {
        "message": {
            "subject": assunto,
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
        print(f"[{dia_str}] E-mail matinal enviado ao Victor")
        return True
    else:
        print(f"Erro e-mail: {resp.status_code} {resp.text[:200]}", file=sys.stderr)
        return False


if __name__ == "__main__":
    msg = gerar_mensagem()
    enviar_telegram(msg)
    enviar_email(msg)
