#!/usr/bin/env python3
"""
Relatório semanal de licitações PNCP — entrega ao Alê (PCS).
Cron: segunda 9h BRT (12h UTC), com lock semanal.

Pós-FASE 5:
1. Email para alexandre@pcsengenharia.com.br → MANTIDO automático,
   mas via helper canônico msgraph_email.py em vez de chamar Graph
   API direto. Classificado como envio pré-autorizado:
   destinatário fixo, cadência fixa (seg 9h), template estável.
   Domínio: PCS (licitações públicas).
2. Em paralelo, envia payload à Flávia (com summary + cards parsed)
   para visibilidade interna e potencial delegação ao agente `pcs`
   se ela detectar necessidade de voz institucional ou bloqueio.

Flags:
  --to <email>      override do destinatário
  --force           ignora janela e lock semanal
  --dry-run         não envia email; mostra preview no stderr
  --skip-email      só envia payload à Flávia
"""

import json, sys, os, subprocess, argparse
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from send_to_flavia import send_to_flavia  # noqa: E402

BRT = timezone(timedelta(hours=-3))
SENDER      = "flavia@mensuraengenharia.com.br"
EMAIL_ACCOUNT = "mensura"
DESTINATARIO_PADRAO = "alexandre@pcsengenharia.com.br"
DIA_ENVIO_SEMANA = 0  # segunda
HORA_ENVIO_BRT = 9
MINUTO_ENVIO_BRT = 0
JANELA_MINUTOS = 20
LOCK_DIR = os.path.expanduser("/root/.openclaw/workspace/.state")

HELPER_EMAIL = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "msgraph_email.py"
)

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

def html_to_plain(html):
    """Conversão crua de HTML em texto plano (preserva carregamento de cards)."""
    import re
    # 1. remover blocos <style>, <script> e seus conteúdos
    text = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script\b[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<head\b[^>]*>.*?</head>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # 2. quebras semânticas
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>', '\n', text)
    text = re.sub(r'</h[1-6]>', '\n\n', text)
    text = re.sub(r'</div>', '\n', text)
    # 3. remover demais tags
    text = re.sub(r'<[^>]+>', '', text)
    # 4. normalizar espaços
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def enviar_email_pre_autorizado(corpo, subject, to, dry_run):
    """Chama msgraph_email.py como helper canônico de envio."""
    if dry_run:
        print("--- [DRY RUN] Email NÃO enviado ---", file=sys.stderr)
        print(f"to:      {to}", file=sys.stderr)
        print(f"user:    {SENDER}", file=sys.stderr)
        print(f"subject: {subject}", file=sys.stderr)
        print("--- corpo (primeiras 800 chars) ---", file=sys.stderr)
        print(corpo[:800], file=sys.stderr)
        print("--- fim ---", file=sys.stderr)
        return 0
    cmd = [
        "python3", HELPER_EMAIL, "send",
        "--account", EMAIL_ACCOUNT,
        "--user", SENDER,
        "--to", to,
        "--subject", subject,
        "--body", corpo,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print("Timeout no envio de email pelo helper", file=sys.stderr)
        return 1
    if r.stdout:
        sys.stderr.write(r.stdout)
    if r.stderr:
        sys.stderr.write(r.stderr)
    return r.returncode

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


def montar_resumo_para_flavia(cards, agora):
    """Resumo executivo curto para a Flávia (texto, não HTML)."""
    if not cards:
        return f"📋 Licitações ({agora.strftime('%d/%m/%Y')}): 0 em aberto."
    linhas = [f"📋 Licitações ({agora.strftime('%d/%m/%Y')}): {len(cards)} em aberto."]
    urgentes = [c for c in cards if 'HOJE' in (c.get('prazo') or '') or 'AMANHÃ' in (c.get('prazo') or '')]
    if urgentes:
        linhas.append(f"\n⚠️ {len(urgentes)} URGENTE(s):")
        for c in urgentes[:5]:
            linhas.append(f"  - {c.get('titulo','?')} | {c.get('local','?')} | {c.get('prazo','?')}")
    linhas.append("\nTop 5 por relevância:")
    for c in cards[:5]:
        linhas.append(f"  • {c.get('titulo','?')} | {c.get('orgao','?')} | {c.get('valor','?')} | {c.get('prazo','?')}")
    return "\n".join(linhas)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--to", default=DESTINATARIO_PADRAO, help="Destinatário do email")
    p.add_argument("--force", action="store_true",
                   help="Ignora janela e lock semanal")
    p.add_argument("--dry-run", action="store_true",
                   help="Não envia email; mostra preview no stderr")
    p.add_argument("--skip-email", action="store_true",
                   help="Só envia payload à Flávia; não tenta email")
    args = p.parse_args()

    agora = datetime.now(BRT)
    if not args.force and not dentro_da_janela_programada(agora):
        print("⏭️ Envio bloqueado: fora da janela semanal permitida (segunda 09:00 BRT).", file=sys.stderr)
        return 0
    if not args.force and ja_enviado_na_semana(agora):
        print("⏭️ Envio bloqueado: relatório semanal já enviado nesta semana.", file=sys.stderr)
        return 0

    print("📡 Gerando relatório de licitações...", file=sys.stderr)

    relatorio_txt = gerar_relatorio_txt()
    cards = parsear_cards(relatorio_txt)
    print(f"   {len(cards)} licitações encontradas.", file=sys.stderr)

    html    = montar_html(cards, agora)
    subject = f"📋 Licitações Construção Civil — {agora.strftime('%d/%m/%Y')} ({len(cards)} em aberto)"
    resumo  = montar_resumo_para_flavia(cards, agora)

    payload = {
        "source": "licitacoes_email.py",
        "kind": "relatorio_semanal_licitacoes",
        "project": None,
        "company": "PCS",
        "domain": "licitacoes_publicas",
        "urgency": "high" if any('HOJE' in (c.get('prazo') or '') or 'AMANHÃ' in (c.get('prazo') or '') for c in cards) else "normal",
        "scheduled_at": agora.isoformat(),
        "totals": {"licitacoes_abertas": len(cards)},
        "body": resumo,
        "external_action": {
            "kind": "email",
            "policy": "pre_authorized_routine",
            "to": args.to,
            "from": SENDER,
            "subject": subject,
            "dry_run": args.dry_run,
            "skipped": args.skip_email,
        },
    }
    rc_flavia = send_to_flavia(payload)

    if args.skip_email:
        return rc_flavia

    corpo_email = html_to_plain(html)
    rc_email = enviar_email_pre_autorizado(corpo_email, subject, args.to, args.dry_run)

    if rc_email == 0 and not args.dry_run:
        registrar_envio_semana(agora, args.to)

    return max(rc_flavia, rc_email)


if __name__ == "__main__":
    sys.exit(main())
