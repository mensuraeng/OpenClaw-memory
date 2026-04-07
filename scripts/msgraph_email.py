#!/usr/bin/env python3
"""
Microsoft Graph API - Gerenciador de E-mails
Uso: email.py <comando> [opções]
"""

import json, sys, os, argparse, re
import urllib.request, urllib.parse, urllib.error

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json")
ACCOUNT_CONFIG_MAP = {
    "mensura": os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json"),
    "mia": os.path.expanduser("~/.openclaw/workspace/config/ms-graph-mia.json"),
}

def load_config(config_path=None, account=None):
    if config_path:
        path = os.path.expanduser(config_path)
    elif account:
        key = account.strip().lower()
        if key not in ACCOUNT_CONFIG_MAP:
            raise SystemExit(f"Conta inválida: {account}. Use: {', '.join(sorted(ACCOUNT_CONFIG_MAP))}")
        path = ACCOUNT_CONFIG_MAP[key]
    else:
        path = DEFAULT_CONFIG_FILE
    with open(path) as f:
        return json.load(f)

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

def graph_request(token, path, method="GET", body=None):
    url = f"https://graph.microsoft.com/v1.0{path}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            if r.status in (202, 204):
                return {}
            content = r.read()
            if not content:
                return {}
            return json.loads(content)
    except urllib.error.HTTPError as e:
        print(f"Erro {e.code}: {e.read().decode()}")
        sys.exit(1)

def list_emails(token, user, folder="inbox", limit=10):
    data = graph_request(token, f"/users/{user}/mailFolders/{folder}/messages?$top={limit}&$orderby=receivedDateTime%20desc&$select=id,subject,from,receivedDateTime,isRead,bodyPreview")
    msgs = data.get("value", [])
    if not msgs:
        print("Nenhuma mensagem encontrada.")
        return
    for m in msgs:
        status = "📩" if not m.get("isRead") else "📧"
        sender = m.get("from", {}).get("emailAddress", {}).get("address", "?")
        date = m.get("receivedDateTime", "")[:16].replace("T", " ")
        print(f"{status} [{m['id'][:8]}...] {date} | De: {sender}")
        print(f"   Assunto: {m.get('subject', '(sem assunto)')}")
        print(f"   {m.get('bodyPreview','')[:100]}")
        print()

def read_email(token, user, msg_id):
    m = graph_request(token, f"/users/{user}/messages/{msg_id}?$select=subject,from,toRecipients,receivedDateTime,body")
    print(f"De: {m['from']['emailAddress']['address']}")
    print(f"Para: {', '.join(r['emailAddress']['address'] for r in m.get('toRecipients', []))}")
    print(f"Data: {m.get('receivedDateTime','')[:16].replace('T',' ')}")
    print(f"Assunto: {m.get('subject','')}")
    print("-" * 60)
    body = m.get("body", {})
    if body.get("contentType") == "text":
        print(body.get("content", ""))
    else:
        text = re.sub(r'<[^>]+>', '', body.get("content", ""))
        print(text[:2000])

def parse_recipients(value):
    if not value:
        return []
    if isinstance(value, list):
        items = value
    else:
        items = [value]
    recipients = []
    for item in items:
        recipients.extend([addr.strip() for addr in item.split(",") if addr.strip()])
    return [{"emailAddress": {"address": addr}} for addr in recipients]

def send_email(token, user, to, subject, body, cc=None):
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": parse_recipients(to)
        }
    }
    cc_recipients = parse_recipients(cc)
    if cc_recipients:
        payload["message"]["ccRecipients"] = cc_recipients
    graph_request(token, f"/users/{user}/sendMail", method="POST", body=payload)
    cc_text = ""
    if cc_recipients:
        cc_text = " | CC: " + ", ".join(r["emailAddress"]["address"] for r in cc_recipients)
    print(f"✅ E-mail enviado para {to}{cc_text}")

def move_email(token, user, msg_id, dest_folder):
    folders = graph_request(token, f"/users/{user}/mailFolders?$select=id,displayName")
    folder_map = {f["displayName"].lower(): f["id"] for f in folders.get("value", [])}
    dest_id = folder_map.get(dest_folder.lower(), dest_folder)
    graph_request(token, f"/users/{user}/messages/{msg_id}/move", method="POST", body={"destinationId": dest_id})
    print(f"✅ Mensagem movida para '{dest_folder}'")

def list_folders(token, user):
    data = graph_request(token, f"/users/{user}/mailFolders?$select=displayName,totalItemCount,unreadItemCount")
    for f in data.get("value", []):
        print(f"📁 {f['displayName']} (total: {f['totalItemCount']}, não lidos: {f['unreadItemCount']})")

def main():
    p = argparse.ArgumentParser(description="Gerenciador de e-mail Microsoft Graph")
    p.add_argument("cmd", choices=["list","read","send","move","folders"], help="Comando")
    p.add_argument("--account", choices=["mensura","mia"], help="Conta/config a usar")
    p.add_argument("--config", help="Caminho explícito do arquivo de configuração")
    p.add_argument("--user", default="alexandre@mensuraengenharia.com.br")
    p.add_argument("--folder", default="inbox")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--id", help="ID da mensagem")
    p.add_argument("--to", help="Destinatário")
    p.add_argument("--subject", help="Assunto")
    p.add_argument("--body", help="Corpo do e-mail")
    p.add_argument("--body-file", help="Arquivo texto com o corpo do e-mail")
    p.add_argument("--cc", action="append", help="Destinatários em cópia (aceita múltiplos --cc ou lista separada por vírgula)")
    p.add_argument("--dest", help="Pasta destino (para mover)")
    args = p.parse_args()

    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            args.body = f.read()

    cfg = load_config(config_path=args.config, account=args.account)
    token = get_token(cfg)

    if args.cmd == "list":
        list_emails(token, args.user, args.folder, args.limit)
    elif args.cmd == "read":
        if not args.id: print("--id obrigatório"); sys.exit(1)
        read_email(token, args.user, args.id)
    elif args.cmd == "send":
        if not all([args.to, args.subject, args.body]):
            print("--to, --subject e --body são obrigatórios"); sys.exit(1)
        send_email(token, args.user, args.to, args.subject, args.body, args.cc)
    elif args.cmd == "move":
        if not args.id or not args.dest:
            print("--id e --dest são obrigatórios"); sys.exit(1)
        move_email(token, args.user, args.id, args.dest)
    elif args.cmd == "folders":
        list_folders(token, args.user)

if __name__ == "__main__":
    main()
