#!/usr/bin/env python3
"""
Envia relatório de licitações PNCP por email via Microsoft Graph.
Uso: python3 licitacoes_email.py [--to email@dest.com] [--force]
"""

import json, sys, os, subprocess, argparse, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))
CONFIG_FILE = os.path.expanduser("/root/.openclaw/workspace/config/ms-graph.json")
SENDER      = "flavia@mensuraengenharia.com.br"
DESTINATARIO_PADRAO = "alexandre@pcsengenharia.com.br"
DIA_ENVIO_SEMANA = 0  # segunda
HORA_ENVIO_BRT = 9
MINUTO_ENVIO_BRT = 0
JANELA_MINUTOS = 20
LOCK_DIR = os.path.expanduser("/root/.openclaw/workspace/.state")

def get_token(cfg):
    url = f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        "client_id": cfg["clientId"],
        "client_secret": cfg["clientSecret"],
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }).encode()
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.load(r)["access_token"]

def gerar_relatorio_txt():
    result = subprocess.run(
        ["python3", "/root/.openclaw/workspace/scripts/monitor_licitacoes.py", "--valores"],
        capture_output=True, text=True, timeout=300
    )
    if result.returncode != 0:
        print(f"Erro ao gerar relatório: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    return result.stdout

def parsear_cards(relatorio_txt):
    linhas = relatorio_txt.split('\n')
    cards = []
    card_atual = {}
    for linha in linhas:
        num = linha.lstrip('#').strip().split(' ')[0].rstrip('.')
        if linha.startswith('#') and num.isdigit():
            if card_atual:
                cards.append(card_atual)
            card_atual = {'titulo': linha.strip()}
        elif '   Órgão:' in linha:
            card_atual['orgao'] = linha.split('Órgão:')[1].strip()
        elif '   Local:' in linha:
            card_atual['local'] = linha.split('Local:')[1].strip()
        elif '   Modalidade:' in linha:
            card_atual['modalidade'] = linha.split('Modalidade:')[1].strip()
        elif '   Valor:' in linha:
            card_atual['valor'] = linha.split('Valor:')[1].strip()
        elif '   Prazo:' in linha:
            card_atual['prazo'] = linha.split('Prazo:')[1].strip()
        elif '   PNCP:' in linha:
            card_atual['pncp'] = linha.split('PNCP:')[1].strip()
        elif '   Objeto:' in linha:
            card_atual['objeto'] = linha.split('Objeto:')[1].strip()
        elif '   🔗' in linha:
            card_atual['url'] = linha.split('🔗')[1].strip()
    if card_atual:
        cards.append(card_atual)
    return cards

def montar_html(cards, agora):
    html = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: Arial, sans-serif; font-size: 14px; color: #222; max-width: 900px; margin: 0 auto; padding: 16px; }}
  h1 {{ color: #1a3c6e; border-bottom: 2px solid #1a3c6e; padding-bottom: 8px; }}
  h2 {{ color: #1a3c6e; font-size: 13px; margin: 0 0 4px 0; }}
  h3.estado {{ background: #1a3c6e; color: white; padding: 6px 14px; border-radius: 6px; margin: 28px 0 10px 0; font-size: 14px; }}
  .card {{ border: 1px solid #ddd; border-radius: 6px; padding: 12px 16px; margin-bottom: 10px; background: #fafafa; }}
  .card.urgente {{ border-left: 4px solid #c0392b; background: #fff5f5; }}
  .card.atencao {{ border-left: 4px solid #e67e22; background: #fffaf5; }}
  .card.normal {{ border-left: 4px solid #2980b9; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; margin-bottom: 4px; }}
  .badge-red {{ background: #c0392b; color: white; }}
  .badge-orange {{ background: #e67e22; color: white; }}
  .meta {{ font-size: 12px; color: #555; margin: 3px 0; }}
  .valor {{ font-size: 13px; font-weight: bold; color: #1a3c6e; }}
  .objeto {{ font-size: 12px; color: #444; margin: 6px 0 4px 0; font-style: italic; }}
  a {{ color: #1a3c6e; font-size: 12px; }}
  .total {{ background: #1a3c6e; color: white; padding: 6px 14px; border-radius: 6px; display: inline-block; margin-bottom: 20px; font-weight: bold; }}
  .rodape {{ font-size: 11px; color: #888; margin-top: 20px; border-top: 1px solid #eee; padding-top: 8px; }}
</style>
</head>
<body>
<h1>📋 Relatório de Licitações — Construção Civil</h1>
<p><em>Gerenciamento de Obras · Fiscalização · Supervisão · Manutenção</em></p>
<p>Gerado em: {agora.strftime('%d/%m/%Y %H:%M')} BRT · Fonte: PNCP</p>
<p class="total">🔎 {len(cards)} licitações em aberto</p>
'''

    # Agrupar por UF — SP primeiro, resto em ordem alfabética
    from collections import defaultdict
    por_uf = defaultdict(list)
    for c in cards:
        local = c.get('local', '')
        uf = local.split('/')[-1].strip() if '/' in local else ''
        por_uf[uf].append(c)

    ufs_ordenadas = sorted(por_uf.keys(), key=lambda u: ('0' if u == 'SP' else u))

    contador = 0
    for uf in ufs_ordenadas:
        nome_estado = uf if uf else 'Não informado'
        qtd = len(por_uf[uf])
        html += f'<h3 class="estado">📍 {nome_estado} &nbsp;·&nbsp; {qtd} licitação{"" if qtd==1 else "ões"}</h3>\n'

        for c in por_uf[uf]:
            contador += 1
            prazo = c.get('prazo', '')
            valor = c.get('valor', '—')
            css = 'normal'
            badge = ''
            if 'HOJE' in prazo or 'AMANHÃ' in prazo:
                css = 'urgente'
                badge = '<span class="badge badge-red">⚠️ URGENTE</span> '
            elif any(f'{i} dias' in prazo for i in range(2, 6)):
                css = 'atencao'
                badge = '<span class="badge badge-orange">⏳ ATENÇÃO</span> '

            obj    = c.get('objeto', '').replace('<', '&lt;').replace('>', '&gt;')
            titulo = c.get('titulo', '').replace('<', '&lt;').replace('>', '&gt;')
            orgao  = c.get('orgao', '').replace('<', '&lt;').replace('>', '&gt;')

            html += f'''<div class="card {css}">
  <h2>#{contador} {titulo}</h2>
  {badge}
  <div class="meta">🏛 {orgao} | 📍 {c.get('local','')} | {c.get('modalidade','')}</div>
  <div class="meta valor">💰 Valor estimado: {valor}</div>
  <div class="meta">⏰ Prazo: {prazo}</div>
  <div class="meta">📄 PNCP: {c.get('pncp','')}</div>
  <div class="objeto">{obj}</div>
  <a href="{c.get('url','#')}" target="_blank">🔗 Ver edital no PNCP</a>
</div>
'''

    html += '''<div class="rodape">
Relatório gerado automaticamente por Flávia | MENSURA Engenharia<br>
Fonte: PNCP — Portal Nacional de Contratações Públicas (pncp.gov.br)
</div>
</body></html>'''
    return html

def enviar_email(token, to, subject, html):
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": html},
            "toRecipients": [{"emailAddress": {"address": to}}],
            "from": {"emailAddress": {"address": SENDER}}
        },
        "saveToSentItems": True
    }
    api_url = f"https://graph.microsoft.com/v1.0/users/{SENDER}/sendMail"
    body_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=body_bytes,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            print(f"✅ Email enviado para {to} ({r.status})")
    except urllib.error.HTTPError as e:
        print(f"❌ Erro {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)

def dentro_da_janela_programada(agora):
    if agora.weekday() != DIA_ENVIO_SEMANA:
        return False
    alvo = agora.replace(hour=HORA_ENVIO_BRT, minute=MINUTO_ENVIO_BRT, second=0, microsecond=0)
    delta_min = abs((agora - alvo).total_seconds()) / 60
    return delta_min <= JANELA_MINUTOS

def lock_path(agora):
    os.makedirs(LOCK_DIR, exist_ok=True)
    return os.path.join(LOCK_DIR, f"licitacoes_email_sent_{agora.strftime('%G-W%V')}.lock")

def ja_enviado_na_semana(agora):
    return os.path.exists(lock_path(agora))

def registrar_envio_semana(agora, destinatario):
    with open(lock_path(agora), "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "sentAt": agora.isoformat(),
            "to": destinatario,
        }, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--to", default=DESTINATARIO_PADRAO, help="Destinatário do email")
    p.add_argument("--force", action="store_true", help="Ignora trava de agenda e envia mesmo fora da janela semanal")
    args = p.parse_args()

    agora = datetime.now(BRT)
    if not args.force and not dentro_da_janela_programada(agora):
        print("⏭️ Envio bloqueado: fora da janela semanal permitida (segunda 09:00 BRT).", file=sys.stderr)
        return
    if not args.force and ja_enviado_na_semana(agora):
        print("⏭️ Envio bloqueado: relatório semanal já enviado nesta semana.", file=sys.stderr)
        return

    print(f"📡 Gerando relatório de licitações...", file=sys.stderr)

    cfg   = json.load(open(CONFIG_FILE))
    token = get_token(cfg)

    relatorio_txt = gerar_relatorio_txt()
    cards = parsear_cards(relatorio_txt)

    print(f"   {len(cards)} licitações encontradas.", file=sys.stderr)

    html    = montar_html(cards, agora)
    subject = f"📋 Licitações Construção Civil — {agora.strftime('%d/%m/%Y')} ({len(cards)} em aberto)"

    enviar_email(token, args.to, subject, html)
    registrar_envio_semana(agora, args.to)

if __name__ == "__main__":
    main()
