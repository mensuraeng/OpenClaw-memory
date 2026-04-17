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
    # ── SEMANA 1 ── 02-07/04
    "2026-04-02": [
        "1ª Onda em andamento — testes elétrica, voltagem e tomadas (Suíte 3, Suíte 2, Suíte 1)",
        "Documentar situação do baldrame com fotos + solução proposta no grupo",
        "Alinhar empresa de drenagem: início confirmado para seg 06/04",
        "Solução paliativa no baldrame: lona + brita na área sem fundação",
        "Luminárias removidas na Circulação Íntima (BRB executando rodateto)",
        "RDO do dia antes das 15h",
    ],
    "2026-04-03": [
        "1ª Onda: continuação elétrica Suíte 3 + Suíte 2 + Suíte 1",
        "Banho 03: checklist em andamento (27 itens, exceto pintura)",
        "Banho 02: checklist em andamento (17 itens, exceto pintura)",
        "Sala de Jantar: checklist em andamento (22 itens)",
        "Confirmar visita Mirim (drywall) para segunda 06/04 às 10h09",
        "RDO do dia antes das 15h",
    ],
    "2026-04-06": [
        "🔵 DRENAGEM INICIA HOJE — acompanhar mobilização da equipe",
        "Visita Mirim (drywall) 10h09 — acompanhar e registrar orçamento",
        "Iniciar elétrica Banho Casal (Banho 03) + Suíte Casal",
        "1ª Onda: checklist Suíte 3 (meta conclusão: qui 09/04)",
        "Banho 01 Crianças: checklist em andamento (17 itens)",
        "Circulação Íntima: checklist em andamento (12 itens)",
        "RDO do dia antes das 15h",
    ],
    "2026-04-07": [
        "🔴 PRAZO CRÍTICO — Enviar mapa de custos de exaustores para aprovação TOOLS",
        "🔴 PRAZO CRÍTICO — Enviar mapa de custos de pintura para aprovação TOOLS",
        "🔴 PRAZO CRÍTICO — Enviar mapa mini-guias + batedores da garagem",
        "🔴 Enviar orçamento de película UV",
        "🔴 Enviar 3 orçamentos gesso/drywall (Mirim + outros 2)",
        "Elétrica Banho Casal em andamento (impermeabilização seg+ter)",
        "1ª Onda: checklist Suíte 3 — DIA CRÍTICO (conclusão amanhã)",
        "RDO do dia antes das 15h",
    ],
    # ── SEMANA 2 ── 08-14/04
    "2026-04-08": [
        "🔴 RECOMPOSIÇÃO DO BALDRAME — DIA 1 de 2",
        "Coordenar equipe baldrame com equipe de drenagem (não interferir)",
        "Elétrica Banho Casal em andamento",
        "✅ META HOJE: Conclusão Suíte 3 (16 itens checklist)",
        "Suíte 2 Hóspede: finalizar checklist (16 itens)",
        "RDO do dia antes das 15h",
    ],
    "2026-04-09": [
        "🔴 RECOMPOSIÇÃO DO BALDRAME — DIA 2 (CONCLUSÃO)",
        "✅ META HOJE: Conclusão Suíte 3 confirmada",
        "✅ META HOJE: Conclusão Banho 02 (Hóspede) — 17 itens",
        "✅ META HOJE: Conclusão Suíte 1 (Crianças) — 9 itens",
        "Drenagem: execução dia 4/15",
        "RDO do dia antes das 15h",
    ],
    "2026-04-10": [
        "🔵 IMPERMEABILIZAÇÃO EXTERNA — DIA 1 de 2",
        "✅ META HOJE: Conclusão Banho 03 (Smaster) — 27 itens",
        "✅ META HOJE: Conclusão Suíte 2 (Hóspede) — 16 itens",
        "Dormitório 4: preparação inicial (início oficial seg 13/04)",
        "Drenagem: execução dia 5/15",
        "RDO do dia antes das 15h",
    ],
    "2026-04-13": [
        "🔵 IMPERMEABILIZAÇÃO EXTERNA — DIA 2 (CONCLUSÃO)",
        "Dormitório 4: início checklist (17 itens, exceto pintura)",
        "Banho 4: início checklist (15 itens, exceto pintura)",
        "Cozinha: início checklist (22 itens, exceto pintura)",
        "Área de Serviço: início checklist (27 itens)",
        "Cozinha/Circulação: início (5 itens)",
        "Acompanhar aprovação TOOLS: exaustores, pintura, mini-guia, batedor, película",
        "Drenagem: execução dia 8/15",
        "RDO do dia antes das 15h",
    ],
    "2026-04-14": [
        "✅ META HOJE: Conclusão Banho 01 (Crianças) — 17 itens",
        "✅ META HOJE: Conclusão Circulação Íntima — 12 itens",
        "🔵 RODAPÉ ÁREA EXTERNA — DIA 1 de 2",
        "Pintura — MOBILIZAÇÃO DIA 1: contratar e alinhar empresa",
        "Limpeza geral — MOBILIZAÇÃO DIA 1",
        "Dormitório 4: checklist em andamento",
        "Drenagem: execução dia 9/15",
        "RDO do dia antes das 15h",
    ],
    # ── SEMANA 3 ── 15-22/04
    "2026-04-15": [
        "🔵 RODAPÉ ÁREA EXTERNA — DIA 2 (CONCLUSÃO)",
        "✅ META HOJE: Área externa concluída (baldrame + impermeabilização + rodapé)",
        "Pintura — mobilização DIA 2",
        "Dormitório 4: checklist em andamento",
        "Drenagem: execução dia 10/15",
        "RDO do dia antes das 15h",
    ],
    "2026-04-16": [
        "✅ META HOJE: Instalação dos exaustores mecânicos",
        "Limpeza especializada de pedras — DIA 1 (duração: 10 dias)",
        "Pintura — mobilização DIA 3 (CONCLUSÃO mobilização)",
        "Dormitório 4: checklist em andamento",
        "Drenagem: execução dia 11/15",
        "RDO do dia antes das 15h",
    ],
    "2026-04-17": [
        "✅ META HOJE: Conclusão Dormitório 4 (17 itens)",
        "✅ META HOJE: Conclusão Banho 4 (15 itens)",
        "✅ META HOJE: Conclusão Cozinha (22 itens)",
        "✅ META HOJE: Conclusão Área de Serviço (27 itens)",
        "✅ META HOJE: Conclusão Cozinha/Circulação (5 itens)",
        "Confirmar pintura mobilizada para segunda 20/04",
        "Drenagem: execução dia 12/15",
        "RDO do dia antes das 15h",
    ],
    "2026-04-20": [
        "🔴 PINTURA GERAL INICIA HOJE — MARCO CRÍTICO SEM FOLGA",
        "Acompanhar mobilização da equipe de pintura (interna + externa)",
        "Mini-guia garagem: início instalação (3 dias: 20-22/04)",
        "Batedor garagem: início instalação (3 dias: 20-22/04)",
        "Garagem: início checklist (6 itens, 14 dias)",
        "Área técnica/pergolado: início checklist (6 + 11 itens)",
        "Drenagem: execução dia 15/15 — CONCLUSÃO PREVISTA",
        "Limpeza especializada de pedras: dia 5/10",
        "RDO do dia antes das 15h",
    ],
    "2026-04-21": [
        "Pintura geral em andamento — DIA 2",
        "Mini-guia garagem: instalação DIA 2",
        "Batedor garagem: instalação DIA 2",
        "Limpeza especializada de pedras: dia 6/10",
        "RDO do dia antes das 15h",
    ],
    "2026-04-22": [
        "Pintura geral em andamento — DIA 3",
        "✅ META HOJE: Conclusão mini-guia garagem",
        "✅ META HOJE: Conclusão batedor garagem",
        "Limpeza especializada de pedras: dia 7/10",
        "RDO do dia antes das 15h",
    ],
    # ── SEMANA 4 ── 23-30/04
    "2026-04-23": [
        "Pintura geral em andamento — DIA 4",
        "Limpeza geral — MOBILIZAÇÃO DIA 1 (5 dias: 23-30/04)",
        "Paisagismo: início (15 dias: 27/04-18/05)",
        "Pedras: preparação início (27/04)",
        "RDO do dia antes das 15h",
    ],
    "2026-04-27": [
        "Pintura geral em andamento — DIA 6",
        "Pedras: início (10 dias: 27/04-11/05)",
        "Paisagismo: início execução",
        "Limpeza geral: mobilização DIA 3",
        "Limpeza especializada de pedras: conclusão (dia 10/10)",
        "RDO do dia antes das 15h",
    ],
    # ── SEMANA 5-6 ── 04-15/05
    "2026-05-04": [
        "Pintura geral em andamento — DIA 11",
        "Limpeza interna: início (10 dias: 04-15/05)",
        "Paisagismo: execução em andamento",
        "Pedras: execução em andamento",
        "RDO do dia antes das 15h",
    ],
    "2026-05-08": [
        "Pintura geral em andamento — DIA 13",
        "✅ META HOJE: Conclusão Garagem + Área Externa completa",
        "Limpeza interna em andamento",
        "Pedras: andamento",
        "RDO do dia antes das 15h",
    ],
    "2026-05-11": [
        "Pintura geral em andamento — DIA 16",
        "✅ META HOJE: Conclusão Pedras",
        "Chuveirão: instalação hoje (1 dia)",
        "Limpeza externa: início (5 dias: 11-15/05)",
        "RDO do dia antes das 15h",
    ],
    "2026-05-15": [
        "✅ META HOJE: Conclusão Pintura Geral (interna + externa) — DIA 19",
        "✅ META HOJE: Conclusão Limpeza Interna",
        "✅ META HOJE: Conclusão Limpeza Externa",
        "Paisagismo: conclusão",
        "Preparar para comissionamento — início segunda 18/05",
        "RDO do dia antes das 15h",
    ],
    # ── SEMANA FINAL ── 18-22/05
    "2026-05-18": [
        "🔵 COMISSIONAMENTO — DIA 1 (5 dias: 18-22/05)",
        "Verificação geral de todos os sistemas: elétrica, hidráulica, exaustores",
        "Checklist final: início item por item",
        "RDO do dia antes das 15h",
    ],
    "2026-05-22": [
        "🏁 ENTREGA DA OBRA — CONCLUSÃO CHECKLIST FINAL",
        "Todos os itens revisados e assinados",
        "As-built documentado",
        "RDO final entregue",
    ],
}

# Prazos críticos — alerta adicional no rodapé da mensagem
PRAZOS_CRITICOS = {
    "2026-04-07": "🔴 HOJE é o prazo final para envio dos 5 mapas/orçamentos ao TOOLS",
    "2026-04-09": "🔴 HOJE: conclusão obrigatória da Suíte 3",
    "2026-04-10": "🟡 HOJE: conclusão Banho 03, Suíte 2, Banho 02, Suíte 1",
    "2026-04-14": "🟡 HOJE: conclusão Banho 01 + Circulação Íntima",
    "2026-04-15": "🟡 HOJE: área externa deve estar concluída",
    "2026-04-16": "🔴 HOJE: exaustores devem ser instalados",
    "2026-04-17": "🟡 HOJE: conclusão 2ª onda completa",
    "2026-04-20": "🔴 HOJE: PINTURA DEVE INICIAR — sem folga no cronograma",
    "2026-05-08": "🟡 HOJE: conclusão garagem + área externa completa",
    "2026-05-15": "🔴 HOJE: pintura + limpeza devem estar concluídas",
    "2026-05-22": "🏁 HOJE: ENTREGA DA OBRA",
}

# ============================================================
def gerar_mensagem():
    hoje_iso = hoje.strftime("%Y-%m-%d")
    
    atividades = ATIVIDADES.get(hoje_iso, [
        "Executar checklists dos ambientes em andamento conforme cronograma",
        "Registrar avanço físico com fotos por ambiente",
        "Documentar qualquer não conformidade ou imprevisto no grupo",
        "Confirmar insumos e materiais necessários para amanhã",
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
