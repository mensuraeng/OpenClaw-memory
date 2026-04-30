#!/usr/bin/env python3
"""Baixa anexos de boletos/faturas da caixa PCS via Microsoft Graph.

Somente leitura: lista mensagens recentes, filtra assuntos/corpos financeiros e baixa anexos.
Não envia, não move, não marca como lido.
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import urllib.error
import html
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONFIG = Path('/root/.openclaw/workspace/config/ms-graph-pcs.json')
DEFAULT_OUT = Path('/root/.openclaw/workspace/finance/boletos/pcs')

KEYWORDS = [
    'boleto', 'fatura', 'cobrança', 'cobranca', 'vencimento', 'segunda via',
    'prazo de pagamento', 'aviso de cobrança', 'aviso de cobranca',
    'duplicata', 'danfe', 'nota fiscal', 'nf-e', 'nfs-e', 'linha digitável',
    'linha digitavel', 'código de barras', 'codigo de barras', 'pix copia e cola', 'documentos', 'confirp', 'darf', 'irpj', 'csll', 'gps', 'fgts', 'inss', 'das'
]
IGNORE = [
    'pagamento confirmado', 'pix recebido', 'pagamento pix recebido',
    'documento aguarda sua assinatura', 'newsletter', 'promoção', 'promocao'
]
BOLETO_RE = re.compile(r'(\d{5}\.\d{5}\s\d{5}\.\d{6}\s\d{5}\.\d{6}\s\d\s\d{14,15})|(\b\d{47,48}\b)')
SAFE_RE = re.compile(r'[^A-Za-z0-9._ -]+')


def safe_name(value: str, fallback='arquivo') -> str:
    value = SAFE_RE.sub('_', value or fallback).strip(' ._-')
    return value[:160] or fallback


def load_config():
    with CONFIG.open() as f:
        return json.load(f)


def get_token(cfg):
    url = f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        'client_id': cfg['clientId'],
        'client_secret': cfg['clientSecret'],
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req) as r:
        return json.load(r)['access_token']


def graph(token, path):
    url = f'https://graph.microsoft.com/v1.0{path}'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise SystemExit(f'Erro Graph {e.code}: {e.read().decode()}')


def paged(token, path):
    while path:
        data = graph(token, path)
        for item in data.get('value', []):
            yield item
        next_url = data.get('@odata.nextLink')
        if next_url:
            path = next_url.split('/v1.0', 1)[1]
        else:
            path = None


def is_candidate(msg):
    subject = (msg.get('subject') or '').lower()
    preview = (msg.get('bodyPreview') or '').lower()
    text = subject + ' ' + preview
    if any(x in text for x in IGNORE):
        return False
    return any(k in text for k in KEYWORDS) or bool(BOLETO_RE.search(text))


def fetch_body(token, user, msg_id):
    m = graph(token, f"/users/{urllib.parse.quote(user)}/messages/{msg_id}?$select=body")
    body = (m.get('body') or {}).get('content') or ''
    return re.sub(r'<[^>]+>', ' ', body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', type=int, default=30)
    ap.add_argument('--out', default=str(DEFAULT_OUT))
    ap.add_argument('--folder', default='inbox')
    ap.add_argument('--limit', type=int, default=100)
    args = ap.parse_args()

    cfg = load_config()
    user = cfg.get('defaultUser') or 'alexandre@pcsengenharia.com.br'
    token = get_token(cfg)
    out_root = Path(args.out) / datetime.now().strftime('%Y-%m-%d_%H%M')
    out_root.mkdir(parents=True, exist_ok=True)

    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).strftime('%Y-%m-%dT%H:%M:%SZ')
    params = urllib.parse.urlencode({
        '$top': str(min(args.limit, 100)),
        '$filter': f'receivedDateTime ge {since}',
        '$orderby': 'receivedDateTime desc',
        '$select': 'id,subject,from,receivedDateTime,bodyPreview,hasAttachments',
    })
    path = f"/users/{urllib.parse.quote(user)}/mailFolders/{urllib.parse.quote(args.folder)}/messages?{params}"

    total_msgs = 0
    candidates = []
    downloaded = []
    no_attachment = []

    for msg in paged(token, path):
        total_msgs += 1
        if not is_candidate(msg):
            continue
        body_text = fetch_body(token, user, msg['id'])
        full_text = f"{msg.get('subject','')} {msg.get('bodyPreview','')} {body_text}"
        if not (is_candidate({'subject': msg.get('subject',''), 'bodyPreview': full_text}) or BOLETO_RE.search(full_text)):
            continue
        candidates.append(msg)

        received = (msg.get('receivedDateTime') or '')[:10]
        sender = ((msg.get('from') or {}).get('emailAddress') or {}).get('address', 'sem-remetente')
        subj = safe_name(msg.get('subject') or 'sem-assunto')
        msg_dir = out_root / f"{received}_{safe_name(sender)}_{subj[:70]}"
        msg_dir.mkdir(parents=True, exist_ok=True)

        links = re.findall(r'https?://[^\s\"<>]+', body_text)
        links = [html.unescape(x).rstrip(').,;') for x in links]
        download_links = [x for x in links if 'DownloadFromEmail' in x or 'download' in x.lower()]

        meta = {
            'id': msg.get('id'),
            'subject': msg.get('subject'),
            'from': sender,
            'receivedDateTime': msg.get('receivedDateTime'),
            'bodyPreview': msg.get('bodyPreview'),
            'linha_digitavel_detectada': (BOLETO_RE.search(full_text).group(0) if BOLETO_RE.search(full_text) else None),
            'download_links': download_links,
        }
        (msg_dir / 'metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')

        # Baixa links diretos disponibilizados no corpo (ex.: Confirp DownloadFromEmail).
        for i, link in enumerate(download_links, 1):
            try:
                req = urllib.request.Request(link, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=60) as r:
                    blob = r.read()
                    cdisp = r.headers.get('Content-Disposition', '')
                    m_name = re.search(r'filename\*?=(?:UTF-8\'\')?\"?([^\";]+)', cdisp, re.I)
                    fname = urllib.parse.unquote(m_name.group(1)) if m_name else f'download_link_{i}'
                    ctype = r.headers.get('Content-Type', '')
                    if '.' not in Path(fname).name:
                        if 'zip' in ctype: fname += '.zip'
                        elif 'pdf' in ctype: fname += '.pdf'
                        else: fname += '.bin'
                    target = msg_dir / safe_name(fname)
                    target.write_bytes(blob)
                    downloaded.append(str(target))
            except Exception as e:
                (msg_dir / f'download_link_{i}_erro.txt').write_text(f'{link}\n{e}\n', encoding='utf-8')

        if not msg.get('hasAttachments'):
            # Ainda salva um txt quando houver linha digitável no corpo.
            if meta['linha_digitavel_detectada']:
                (msg_dir / 'boleto_corpo_email.txt').write_text(full_text[:10000], encoding='utf-8')
                downloaded.append(str(msg_dir / 'boleto_corpo_email.txt'))
            elif not download_links:
                no_attachment.append(meta)
            continue

        att_path = f"/users/{urllib.parse.quote(user)}/messages/{msg['id']}/attachments?$top=50"
        for att in paged(token, att_path):
            if att.get('@odata.type') != '#microsoft.graph.fileAttachment':
                continue
            name = safe_name(att.get('name') or 'anexo')
            content = att.get('contentBytes')
            if not content:
                continue
            target = msg_dir / name
            # Evita sobrescrever nomes repetidos.
            if target.exists():
                stem, suffix = target.stem, target.suffix
                i = 2
                while target.exists():
                    target = msg_dir / f'{stem}_{i}{suffix}'
                    i += 1
            target.write_bytes(base64.b64decode(content))
            downloaded.append(str(target))

    summary = {
        'source': 'baixar_boletos_pcs.py',
        'account': user,
        'folder': args.folder,
        'days': args.days,
        'messages_scanned': total_msgs,
        'candidate_messages': len(candidates),
        'files_downloaded': len(downloaded),
        'output_dir': str(out_root),
        'downloaded': downloaded,
        'no_attachment': no_attachment,
    }
    (out_root / '_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
