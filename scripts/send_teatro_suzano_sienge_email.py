#!/usr/bin/env python3
"""Envia ao Philippe a planilha do Teatro Suzano para upload no Sienge.

Uso seguro:
  python3 scripts/send_teatro_suzano_sienge_email.py --dry-run
  python3 scripts/send_teatro_suzano_sienge_email.py --send
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
import urllib.parse
import urllib.request
import urllib.error

CONFIG = Path('/root/.openclaw/workspace/config/ms-graph.json')
USER = 'flavia@mensuraengenharia.com.br'
ATTACHMENT = Path('/root/.openclaw/workspace/TEATRO_SUZANO_SIENGE_UPLOAD_PRONTO.xlsx')
TO = 'philippe.santos@pcsengenharia.com.br'
CC = ['alexandre@pcsengenharia.com.br']
SUBJECT = 'Teatro Suzano — planilha para importação no Sienge'
BODY = '''Philippe, bom dia.

Segue em anexo a planilha do orçamento do Teatro Suzano tratada para importação no Sienge.

Instruções:
1. Usar a aba “Orçamento” para a importação.
2. A aba “Conferencia” é apenas para auditoria e validação interna.
3. A planilha contém 176 itens válidos, 14 seções e total de R$ 625.085,47.
4. Há 1 item sem código original que foi mantido com código sintético “SEM_CODIGO_001” — “RETIRADA DE CADEIRAS (DESMOBILIZAÇÃO)”.
5. Se o Sienge acusar erro de formato, código, coluna ou importação, por favor responda este e-mail com o erro exibido e mantenha o Alexandre copiado para ajustarmos a planilha no formato exato exigido pelo sistema.

Obrigado.
'''


def load_config():
    return json.loads(CONFIG.read_text(encoding='utf-8'))


def get_token(cfg):
    url = f"https://login.microsoftonline.com/{cfg['tenantId']}/oauth2/v2.0/token"
    data = urllib.parse.urlencode({
        'client_id': cfg['clientId'],
        'client_secret': cfg['clientSecret'],
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials',
    }).encode()
    req = urllib.request.Request(url, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)['access_token']


def recipients(addresses):
    return [{'emailAddress': {'address': a}} for a in addresses]


def build_payload():
    if not ATTACHMENT.exists():
        raise FileNotFoundError(f'Anexo não encontrado: {ATTACHMENT}')
    content_type = mimetypes.guess_type(str(ATTACHMENT))[0] or 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    attachment_content = base64.b64encode(ATTACHMENT.read_bytes()).decode('ascii')
    return {
        'message': {
            'subject': SUBJECT,
            'body': {'contentType': 'Text', 'content': BODY},
            'toRecipients': recipients([TO]),
            'ccRecipients': recipients(CC),
            'attachments': [
                {
                    '@odata.type': '#microsoft.graph.fileAttachment',
                    'name': ATTACHMENT.name,
                    'contentType': content_type,
                    'contentBytes': attachment_content,
                }
            ],
        },
        'saveToSentItems': True,
    }


def send():
    cfg = load_config()
    user = USER
    token = get_token(cfg)
    payload = build_payload()
    url = f'https://graph.microsoft.com/v1.0/users/{user}/sendMail'
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, method='POST', headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    })
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            print(f'ENVIADO status={r.status} from={user} to={TO} cc={",".join(CC)} attachment={ATTACHMENT}')
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        print(f'ERRO status={e.code} body={body}')
        raise SystemExit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--send', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    payload = build_payload()
    if args.dry_run or not args.send:
        cfg = load_config()
        print(json.dumps({
            'from': USER,
            'to': TO,
            'cc': CC,
            'subject': SUBJECT,
            'attachment': str(ATTACHMENT),
            'attachment_size': ATTACHMENT.stat().st_size,
            'body_preview': BODY[:500],
            'payload_has_attachment': bool(payload['message'].get('attachments')),
        }, ensure_ascii=False, indent=2))
        return
    send()


if __name__ == '__main__':
    main()
