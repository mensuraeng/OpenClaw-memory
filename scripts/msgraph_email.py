#!/usr/bin/env python3
"""
Microsoft Graph API - Gerenciador de E-mails
Uso: email.py <comando> [opções]
"""

import json, sys, os, argparse, re
import urllib.request, urllib.parse, urllib.error

CONFIG_FILE = os.path.expanduser("~/.openclaw/workspace/config/ms-graph.json")

def load_config():
    with open(CONFIG_FILE) as f:
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
            if r.status == 204:
                return {}
            return json.load(r)
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

def send_email(token, user, to, subject, body):
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "Text", "content": body},
            "toRecipients": [{"emailAddress": {"address": to}}]
        }
    }
    graph_request(token, f"/users/{user}/sendMail", method="POST", body=payload)
    print(f"✅ E-mail enviado para {to}")

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
    p.add_argument("--user", default="alexandre@mensuraengenharia.com.br")
    p.add_argument("--folder", default="inbox")
    p.add_argument("--limit", type=int, default=10)
    p.add_argument("--id", help="ID da mensagem")
    p.add_argument("--to", help="Destinatário")
    p.add_argument("--subject", help="Assunto")
    p.add_argument("--body", help="Corpo do e-mail")
    p.add_argument("--dest", help="Pasta destino (para mover)")
    args = p.parse_args()

    cfg = load_config()
    token = get_token(cfg)

    if args.cmd == "list":
        list_emails(token, args.user, args.folder, args.limit)
    elif args.cmd == "read":
        if not args.id: print("--id obrigatório"); sys.exit(1)
        read_email(token, args.user, args.id)
    elif args.cmd == "send":
        if not all([args.to, args.subject, args.body]):
            print("--to, --subject e --body são obrigatórios"); sys.exit(1)
        send_email(token, args.user, args.to, args.subject, args.body)
    elif args.cmd == "move":
        if not args.id or not args.dest:
            print("--id e --dest são obrigatórios"); sys.exit(1)
        move_email(token, args.user, args.id, args.dest)
    elif args.cmd == "folders":
        list_folders(token, args.user)

if __name__ == "__main__":
    main()
